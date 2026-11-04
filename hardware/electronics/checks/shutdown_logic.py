"""Stable-state logic evaluation of the actual Hub netlist. No analog or propagation model."""
import xml.etree.ElementTree as ET


class Shutdown:
    def __init__(self,path):
        root=ET.parse(path).getroot()
        self.parts={c.attrib['ref']:c.findtext('value')for c in root.findall('./components/comp')}
        self.pins={(n.attrib['ref'],n.attrib['pin']):net.attrib['name']for net in root.findall('./nets/net')for n in net}
        self.q=[False,False];self.clk=[False,False]

    def net(self,ref,pin):return self.pins[(ref,str(pin))]

    def step(self,control=True,pd=True,ready=False,oc=None,health=None,input_oc=True,input_health=True):
        oc=[True]*6 if oc is None else oc;health=[True]*6 if health is None else health
        values={self.net('U50',7):False,self.net('U50',14):True,
                self.net('U7',1):control,self.net('U5',2):not pd,
                self.net('U52',1):ready,self.net('U4',6):input_oc,self.net('U2',14):input_health}
        for k in range(6):
            values[self.net(f'U{21+2*k}',6)]=oc[k]
            values[self.net(f'U{20+2*k}',14)]=health[k]
        def read(ref,pin):return values.get(self.net(ref,pin))
        def drive(ref,pin,v):values[self.net(ref,pin)]=v
        for _ in range(16):
            for i,(q,nq)in enumerate([(5,6),(9,8)]):drive('U50',q,self.q[i]);drive('U50',nq,not self.q[i])
            for _ in range(24):
                before=dict(values)
                for ref,value in self.parts.items():
                    if value.startswith('SN74LVC1G11'):inputs,out,op=[1,3,6],4,all
                    elif value.startswith('SN74LVC1G08'):inputs,out,op=[1,2],4,all
                    elif value.startswith('SN74LVC1G32'):inputs,out,op=[1,2],4,any
                    elif value.startswith(('SN74LVC1G04','SN74LVC1G14')):inputs,out,op=[2],4,lambda x:not x[0]
                    else:continue
                    args=[read(ref,p)for p in inputs]
                    if None not in args:drive(ref,out,op(args))
                for ref,value in self.parts.items():
                    if value.startswith('SN74HCS11'):
                        for inputs,out in [([1,2,13],12),([3,4,5],6),([9,10,11],8)]:
                            args=[read(ref,p)for p in inputs]
                            if None not in args:drive(ref,out,all(args))
                    elif value.startswith('SN74LVC2G17'):
                        for a,y in [(1,6),(3,4)]:
                            if read(ref,a)is not None:drive(ref,y,read(ref,a))
                if before==values:break
            old=self.q[:]
            for i,(clear,preset,data,clock)in enumerate([(1,4,2,3),(13,10,12,11)]):
                c,p,d,k=(read('U50',pin)for pin in (clear,preset,data,clock))
                if None in (c,p,d,k):raise ValueError('Unresolved latch input')
                if not c and not p:raise ValueError('Both asynchronous controls asserted in stable state')
                if not c:self.q[i]=False
                elif not p:self.q[i]=True
                elif k and not self.clk[i]:self.q[i]=d
                self.clk[i]=k
            if self.q==old:
                return dict(enabled=read('U6',4),fault=self.q[0],armed=self.q[1],
                            port_enables=[read(f'U{20+2*k}',12)for k in range(6)])
        raise ValueError('Latch network did not settle')
