#!/usr/bin/env python3
"""Check the Hub input breaker, six outputs and shared hardware shutdown."""
import argparse
import xml.etree.ElementTree as ET


def inspect(path):
    root=ET.parse(path).getroot()
    names={}
    for net in root.findall('./nets/net'):
        name=net.attrib['name'].rsplit('/',1)[-1]
        for node in net:names[(node.attrib['ref'],node.attrib['pin'])]=name
    expected={
        'U1':{1:'CC1',2:'CC1',4:'CC2',5:'CC2',6:'PD_RESET',7:'PD_SCL',8:'PD_SDA',10:'GND',12:'GND',13:'GND',16:'PD_SINK_EN_N',18:'PD_VBUS_SENSE',19:'PD_ALERT_N',20:'PD_20V_OK_N',21:'PD_1V2',22:'GND',23:'PD_2V7',24:'VBUS_PD',25:'GND'},
        'U2':{1:'EFUSE_IN',2:'EFUSE_IN',3:'B_GATE',4:'B_DRV',5:'INPUT_20V',6:'INPUT_UVLO',7:'INPUT_OVP',8:'GND',9:'INPUT_DVDT',10:'INPUT_ILIM',12:'INPUT_ENABLE',14:'INPUT_FAULT_N',15:'GND',17:'HUB_20V',18:'HUB_20V',25:'GND'},
        'U3':{1:'INPUT_20V',2:'GND',5:'CONTROL_3V3'},
        'U4':{1:'CONTROL_3V3',2:'INPUT_CURRENT',3:'INPUT_LIMIT',4:'GND',5:'CONTROL_GOOD',6:'INPUT_OC_N',7:'INPUT_20V',8:'VBUS_PD'},
        'U5':{2:'PD_20V_OK_N',3:'GND',4:'PD_20V_OK',5:'CONTROL_3V3'},
        'U6':{1:'RUN_OK',2:'GND',3:'CONTROL_GOOD',4:'INPUT_ENABLE',5:'CONTROL_3V3',6:'PD_20V_OK'},
        'U7':{1:'CONTROL_GOOD_RAW',2:'GND',3:'RESET_N',5:'CONTROL_3V3',6:'CONTROL_3V3'},
        'Q1':{1:'INPUT_20V',2:'INPUT_20V',3:'INPUT_20V',4:'B_GATE',5:'EFUSE_IN'},
        'Q2':{1:'B_DRV',2:'INPUT_20V',3:'B_GATE'},
        'R1':{1:'VBUS_PD',2:'PD_VBUS_SENSE'},'R8':{1:'VBUS_PD',2:'INPUT_20V'},
        'R9':{1:'INPUT_20V',2:'INPUT_UVLO'},'R10':{1:'INPUT_UVLO',2:'GND'},
        'R11':{1:'INPUT_20V',2:'INPUT_OVP'},'R12':{1:'INPUT_OVP',2:'GND'},
        'R13':{1:'INPUT_ILIM',2:'GND'},'R14':{1:'INPUT_LIMIT',2:'GND'},
        'R15':{1:'CONTROL_3V3',2:'INPUT_OC_N'},'R16':{1:'CONTROL_3V3',2:'CONTROL_GOOD_RAW'},
        'R17':{1:'CONTROL_3V3',2:'RESET_N'},'R18':{1:'INPUT_ENABLE',2:'GND'},
        'R19':{1:'CONTROL_3V3',2:'INPUT_FAULT_N'},'SW1':{1:'RESET_N',2:'GND'},
        'J2':{1:'CONTROL_3V3',2:'GND',3:'PD_SCL',4:'PD_SDA',5:'PD_RESET',6:'PD_ALERT_N',7:'PD_20V_OK_N',8:'PD_SINK_EN_N'},
    }
    for pin in ('A4','A9','B4','B9'):expected.setdefault('J1',{})[pin]='VBUS_PD'
    for pin in ('A1','A12','B1','B12','SH'):expected['J1'][pin]='GND'
    expected['J1'].update(A5='CC1',B5='CC2')
    for ref,rail in [('C1','VBUS_PD'),('C2','PD_1V2'),('C3','PD_2V7'),('C4','VBUS_PD'),('C5','INPUT_20V'),('C6','HUB_20V'),('C7','EFUSE_IN'),('C8','INPUT_DVDT'),('C14','INPUT_20V')]+[(f'C{i}','CONTROL_3V3')for i in range(9,14)]:
        expected[ref]={1:rail,2:'GND'}
    for ref,net in [('R3','PD_SCL'),('R4','PD_SDA'),('R5','PD_ALERT_N'),('R6','PD_20V_OK_N'),('R7','PD_SINK_EN_N')]:expected[ref]={1:'CONTROL_3V3',2:net}
    expected['R2']={1:'PD_RESET',2:'GND'}
    for i,net in enumerate(['HUB_20V','INPUT_CURRENT','INPUT_OC_N','INPUT_FAULT_N'],1):expected[f'TP{i}']={1:net}
    full_names={(n.attrib['ref'],n.attrib['pin']):net.attrib['name']for net in root.findall('./nets/net')for n in net}
    port_outputs=[];port_inputs=[]
    for k in range(6):
        u=f'U{20+2*k}';m=f'U{21+2*k}';q=f'Q{10+2*k}';b=f'Q{11+2*k}';r=100+20*k;c=100+10*k
        output=f'PORT{k+1}_20V';oc=f'PORT{k+1}_OC_N';health=f'PORT{k+1}_HEALTH_N';mon=f'PORT{k+1}_MON'
        expected[u]={1:'EFUSE_IN',2:'EFUSE_IN',3:'B_GATE',4:'B_DRV',5:'PORT_IN',6:'GND',7:'PORT_OVP',8:'GND',9:'PORT_DVDT',10:'PORT_ILIM',12:'INPUT_ENABLE',14:health,15:'PORT_PGTH',16:health,17:output,18:output,25:'GND'}
        expected[m]={1:'CONTROL_3V3',2:mon,3:'PORT_LIMIT',4:'GND',5:'CONTROL_GOOD',6:oc,7:'PORT_IN',8:'HUB_20V'}
        expected[q]={1:'PORT_IN',2:'PORT_IN',3:'PORT_IN',4:'B_GATE',5:'EFUSE_IN'}
        expected[b]={1:'B_DRV',2:'PORT_IN',3:'B_GATE'}
        expected.update({f'R{r}':{1:'HUB_20V',2:'PORT_IN'},f'R{r+1}':{1:'PORT_LIMIT',2:'GND'},f'R{r+2}':{1:'PORT_ILIM',2:'GND'},f'R{r+3}':{1:'CONTROL_3V3',2:oc},f'R{r+4}':{1:'CONTROL_3V3',2:health},f'R{r+5}':{1:output,2:'PORT_PGTH'},f'R{r+6}':{1:'PORT_PGTH',2:'GND'},f'R{r+7}':{1:'PORT_IN',2:'PORT_OVP'},f'R{r+8}':{1:'PORT_OVP',2:'GND'},f'R{r+9}':{1:'INPUT_ENABLE',2:'GND'},f'R{r+10}':{1:output,2:'GND'}})
        for j,rail in enumerate(['PORT_IN','EFUSE_IN',output,'PORT_DVDT','CONTROL_3V3']):expected[f'C{c+j}']={1:rail,2:'GND'}
        expected[f'D{100+k}']={1:output,2:'GND'}
        expected[f'TP{10+k}']={1:output};expected[f'TP{20+k}']={1:mon}
        port_outputs.append(full_names[(u,'17')]);port_inputs.append(full_names[(u,'5')])
    if len(set(port_outputs))!=6 or len(set(port_inputs))!=6:raise ValueError('Output isolation boundaries are shorted')
    expected['U40']={1:'PORT1_OC_N',2:'PORT2_OC_N',13:'PORT3_OC_N',12:'OC_A',3:'PORT4_OC_N',4:'PORT5_OC_N',5:'PORT6_OC_N',6:'OC_B',9:'OC_A',10:'OC_B',11:'INPUT_OC_N',8:'ALL_OC_RAW_N',7:'GND',14:'CONTROL_3V3'}
    expected['U43']={1:'PORT1_HEALTH_N',2:'PORT2_HEALTH_N',13:'PORT3_HEALTH_N',12:'HEALTH_A',3:'PORT4_HEALTH_N',4:'PORT5_HEALTH_N',5:'PORT6_HEALTH_N',6:'HEALTH_B',9:'HEALTH_A',10:'HEALTH_B',11:'INPUT_FAULT_N',8:'ALL_HEALTH_RAW_N',7:'GND',14:'CONTROL_3V3'}
    expected['U53']={1:'ALL_OC_RAW_N',6:'ALL_OC_N',3:'ALL_HEALTH_RAW_N',4:'ALL_HEALTH_N',2:'GND',5:'CONTROL_3V3'}
    expected.update({'U46':{1:'ALL_HEALTH_N',2:'ARM_N',3:'GND',4:'HEALTH_READY_N',5:'CONTROL_3V3'},'U47':{1:'ALL_OC_N',2:'HEALTH_READY_N',3:'GND',4:'FAULT_SOURCE_N',5:'CONTROL_3V3'},'U48':{1:'FAULT_SOURCE_N',2:'CONTROL_GOOD_N',3:'GND',4:'FAULT_SET_N',5:'CONTROL_3V3'},'U49':{2:'CONTROL_GOOD',3:'GND',4:'CONTROL_GOOD_N',5:'CONTROL_3V3'},'U50':{1:'CONTROL_GOOD',2:'GND',3:'GND',4:'FAULT_SET_N',5:'FAULT_LATCHED',6:'RUN_OK',7:'GND',8:'ARM_N',9:'ARMED',10:'CONTROL_3V3',11:'START_DONE',12:'CONTROL_3V3',13:'CONTROL_GOOD',14:'CONTROL_3V3'},'U51':{1:'START_DONE_RAW',2:'GND',3:'CONTROL_GOOD_RAW',4:'CONTROL_GOOD',5:'CONTROL_3V3',6:'START_DONE'},'U52':{1:'START_DONE_RAW',2:'GND',3:'CONTROL_GOOD',4:'START_CT',5:'INPUT_ENABLE',6:'CONTROL_3V3'},'R302':{1:'CONTROL_3V3',2:'START_DONE_RAW'},'R303':{1:'CONTROL_3V3',2:'START_CT'},'R304':{1:'RUN_OK',2:'GND'},'D8':{1:'HUB_20V',2:'GND'},'R20':{1:'HUB_20V',2:'GND'},'TP30':{1:'FAULT_LATCHED'},'TP31':{1:'ARMED'}})
    for i in (300,303,306,307,308,309,310,311,312,313):expected[f'C{i}']={1:'CONTROL_3V3',2:'GND'}
    checks=0
    for ref,pins in expected.items():
        for pin,net in pins.items():
            actual=names.get((ref,str(pin)))
            if actual!=net:raise ValueError(f'{ref}.{pin}: expected {net}, got {actual}')
            checks+=1
    for ref,pins in {'U2':[11,13,16,19,20,21,22,23,24],'U3':[3,4],'U5':[1],'U7':[4],'U1':[3,9,11,14,15,17]}.items():
        for pin in pins:
            if not names.get((ref,str(pin)),'').startswith('unconnected-'):raise ValueError(f'{ref}.{pin}: missing deliberate no-connect')
            checks+=1
    for k in range(6):
        ref=f'U{20+2*k}'
        for pin in (11,13,19,20,21,22,23,24):
            if not names.get((ref,str(pin)),'').startswith('unconnected-'):raise ValueError(f'{ref}.{pin}: missing deliberate no-connect')
            checks+=1
    components={c.attrib['ref']:c for c in root.findall('./components/comp')}
    values={'R1':'470 1% 2W','R8':'10m 1% 1W','R9':'135k 0.1%','R10':'10k 0.1%','R11':'172k 0.1%','R12':'10k 0.1%','R13':'3k 0.1%','R14':'10.5k 0.1%','C8':'100nF 50V','C9':'10uF 50V X7R','U1':'STUSB4500QTR','U2':'TPS26630RGER','U3':'TPS70933DBVR','U4':'INA301A1IDGKR','U7':'TPS3808G30DBVR'}
    values.update(U5='SN74LVC1G14DBVR',Q2='BSS138LT1G',U40='SN74HCS11PWR',U43='SN74HCS11PWR',U53='SN74LVC2G17DBVR',D8='SMBJ22A-E3/52',R303='100k 1%',U50='SN74LVC74APWR',U51='SN74LVC2G17DBVR',U52='TPS3808G01DBVR',R15='22k 1%',R19='22k 1%')
    for k in range(6):
        r=100+20*k;c=100+10*k
        values.update({f'Q{11+2*k}':'BSS138LT1G',f'D{100+k}':'SMBJ22A-E3/52',f'U{20+2*k}':'TPS26630RGER',f'U{21+2*k}':'INA301A1IDGKR',f'R{r}':'10m 1% 1W',f'R{r+1}':'10k 0.1%',f'R{r+2}':'3k 0.1%',f'R{r+3}':'22k 1%',f'R{r+4}':'22k 1%',f'R{r+5}':'130k 0.1%',f'R{r+6}':'10k 0.1%',f'R{r+7}':'172k 0.1%',f'R{r+8}':'10k 0.1%',f'R{r+9}':'10k 1%',f'R{r+10}':'10k 1% 0.25W',f'C{c+3}':'22nF 50V C0G'})
    for ref,value in values.items():
        if components[ref].findtext('value')!=value:raise ValueError(f'{ref}: calculation value changed')
        checks+=1
    for ref,c in components.items():
        if not c.findtext('footprint'):raise ValueError(f'{ref}: no footprint')
        checks+=1
    return checks,len(components),len(root.findall('./nets/net'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('netlist');args=p.parse_args()
    checks,parts,nets=inspect(args.netlist)
    print(f'PASS: {checks} Hub connectivity/value checks; {parts} components; {nets} nets.')
