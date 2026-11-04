#!/usr/bin/env python3
"""Check Rev A connectivity in native KiCad XML. Does not verify component behavior or qualification."""
import argparse
import xml.etree.ElementTree as ET


def inspect(path):
    root = ET.parse(path).getroot()
    nets, members = {}, {}
    for net in root.findall('./nets/net'):
        name = net.attrib['name'].removeprefix('/')
        members[name] = set()
        for node in net.findall('node'):
            key = (node.attrib['ref'],node.attrib['pin'])
            if key in nets:
                raise ValueError(f'Duplicate pin in netlist: {key}')
            nets[key] = name
            members[name].add(key)
    checks = 0

    def expect(ref,pin,name):
        nonlocal checks
        actual = nets.get((ref,str(pin)))
        if actual != name:
            raise ValueError(f'{ref}.{pin}: expected {name}, got {actual}')
        checks += 1

    def disconnected(ref,pin):
        nonlocal checks
        if 'unconnected-' not in nets.get((ref,str(pin)),''):
            raise ValueError(f'{ref}.{pin}: expected a deliberate no-connect')
        checks += 1

    mcu={2:'+3V3',3:'MODULE_20V_EN',4:'MODULE_20V_FAULT',5:'BUS_SENSE',6:'N_DETECT',
         7:'E_TX',8:'E_RX',9:'E_DETECT',10:'MODULE_5V_FAULT',11:'MODULE_ID',12:'RGB_DATA',
         13:'W_TX',14:'S_TX',15:'S_RX',16:'W_RX',17:'MODULE_IO_REQUEST',18:'MODULE_5V_EN',
         19:'EDGE_IO_DISABLE',20:'LOCAL_POWER_FAULT',21:'N_TX',22:'N_RX',23:'MODULE_CTRL',
         24:'DEBUG_DCK',25:'DEBUG_DIO',26:'MODULE_SCL',27:'MODULE_SDA',29:'GND'}
    for pin,name in mcu.items():expect('U1',pin,name)
    for ref,d,reverse in [('J3','N',False),('J6','E',False),('J4','S',True),('J5','W',True)]:
        detect=d+'_DETECT'+('_EDGE' if d in 'NE' else '')
        order=[d+'_20V','GND',d+'_TX_EDGE',d+'_RX_EDGE',detect]
        if reverse:order=[detect,d+'_TX_EDGE',d+'_RX_EDGE','GND',d+'_20V']
        for pin,name in enumerate(order,1):expect(ref,pin,name)
    for pin,name in enumerate(['GND','MODULE_5V','MODULE_20V','MODULE_SDA_PAD','MODULE_SCL_PAD',
                                'MODULE_CTRL_PAD','MODULE_ID_PAD','GND'],1):expect('J7',pin,name)
    groups={
        'U4':{1:'GND',2:'TILE_20V',3:'BUCK_EN',5:'BUCK_FB',6:'BUCK_VCC',7:'BUCK_BST',8:'BUCK_SW',9:'GND'},
        'U5':{1:'TILE_20V',2:'TILE_20V',3:'MODULE_RTN',5:'EFUSE_OVLO',6:'MODULE_MODE',7:'MODULE_20V_SHDN',8:'MODULE_RTN',9:'GND',11:'EFUSE_ILM',12:'EFUSE_DVDT',14:'MODULE_20V_FAULT',15:'MODULE_20V',16:'MODULE_20V',17:'MODULE_RTN'},
        'U7':{1:'LOCAL_20V_RAW',2:'LOCAL_20V_RAW',3:'LOCAL_RTN',5:'LOCAL_OVP',6:'LOCAL_MODE',8:'LOCAL_RTN',9:'GND',11:'LOCAL_ILIM',12:'LOCAL_DVDT',14:'LOCAL_POWER_FAULT',15:'TILE_20V',16:'TILE_20V',17:'LOCAL_RTN'},
        'U3':{1:'MODULE_5V_EN',2:'MODULE_5V_OVLO',4:'MODULE_5V_FAULT',5:'+5V',6:'MODULE_5V',7:'MODULE_5V_DVDT',8:'GND',9:'MODULE_5V_ILIM'},
        'U6':{1:'GND',2:'RGB_DATA',3:'GND',4:'RGB_BUFFER_OUT',5:'+5V'},
        'U12':{1:'MODULE_IO_ENABLE',2:'MODULE_SCL',3:'MODULE_SCL_PAD',4:'MODULE_IO_ENABLE',5:'MODULE_SDA',6:'MODULE_SDA_PAD',7:'GND',8:'MODULE_CTRL_PAD',9:'MODULE_CTRL',10:'MODULE_IO_ENABLE',11:'MODULE_ID_PAD',12:'MODULE_ID',13:'+3V3',14:'+3V3'},
        'U13':{1:'+3V3',2:'BUS_SENSE_RAW',3:'BUS_SENSE',4:'+3V3',5:'N_DETECT_EDGE',6:'N_DETECT',7:'GND',8:'E_DETECT',9:'E_DETECT_EDGE',10:'+3V3',13:'GND',14:'+3V3'},
        'U14':{1:'MODULE_5V_GOOD',2:'GND',3:'+3V3',5:'MODULE_5V_SENSE',6:'+3V3'},
        'U15':{1:'MODULE_5V_GOOD',2:'MODULE_IO_REQUEST',3:'GND',4:'MODULE_IO_ENABLE',5:'+3V3'},
        'F1':{1:'BUS_20V',2:'LOCAL_20V_RAW'}, 'L1':{1:'BUCK_SW',2:'+5V'},
        'C10':{1:'BUCK_BST',2:'BUCK_SW'},'C24':{1:'BUCK_VCC',2:'GND'},
        'D1':{1:'+5V',2:'RGB_CHAIN',3:'GND',4:'RGB_DIN'},
        'D3':{1:'+5V',2:'RGB_DOUT_TEST',3:'GND',4:'RGB_CHAIN'},
        'R3':{1:'RGB_BUFFER_OUT',2:'RGB_DIN'},
        'R11':{1:'TILE_20V',2:'BUS_SENSE_RAW'},'R12':{1:'BUS_SENSE_RAW',2:'GND'},
        'R15':{1:'MODULE_20V_SHDN',2:'MODULE_RTN'}, 'R16':{1:'EFUSE_ILM',2:'MODULE_RTN'},
        'R18':{1:'EFUSE_OVLO',2:'MODULE_RTN'},'C17':{1:'EFUSE_DVDT',2:'MODULE_RTN'},
        'R21':{1:'LOCAL_ILIM',2:'LOCAL_RTN'},'R22':{1:'LOCAL_MODE',2:'LOCAL_RTN'},
        'R23':{1:'MODULE_MODE',2:'MODULE_RTN'},'R24':{1:'MODULE_20V_EN',2:'MODULE_20V_SHDN'},
        'R25':{1:'LOCAL_20V_RAW',2:'LOCAL_OVP'},'R26':{1:'LOCAL_OVP',2:'LOCAL_RTN'},
        'R28':{1:'+5V',2:'BUCK_FB'},'R29':{1:'BUCK_FB',2:'GND'},
        'R46':{1:'+3V3',2:'EDGE_IO_DISABLE'},'R47':{1:'MODULE_IO_REQUEST',2:'GND'},
        'R48':{1:'+3V3',2:'MODULE_5V_GOOD'},'R49':{1:'MODULE_5V',2:'GND'},
        'R50':{1:'+3V3',2:'GND'},'R51':{1:'MODULE_5V',2:'MODULE_5V_SENSE'},
        'R52':{1:'MODULE_5V_SENSE',2:'GND'},'R53':{1:'MODULE_5V_ILIM',2:'GND'},'R54':{1:'+5V',2:'MODULE_5V_OVLO'},'R55':{1:'MODULE_5V_OVLO',2:'GND'},'C33':{1:'MODULE_5V_DVDT',2:'GND'},
    }
    for i,d in enumerate('NESW'):
        groups['U'+str(i+8)]={1:'EDGE_IO_DISABLE',2:d+'_TX',3:d+'_RX',4:'GND',5:d+'_RX_IN',6:d+'_TX_DRV',7:'EDGE_IO_DISABLE',8:'+3V3'}
        for j,(a,b) in enumerate([(d+'_TX_DRV',d+'_TX_EDGE'),(d+'_RX_EDGE',d+'_RX_IN'),('+3V3',d+'_TX'),('+3V3',d+'_RX_IN')]):
            groups['R'+str(30+i*4+j)]={1:a,2:b}
    for ref,pins in groups.items():
        for pin,name in pins.items():expect(ref,pin,name)
    for ref,d in [('F2','N'),('F3','E'),('F4','S'),('F5','W')]:
        expect(ref,1,d+'_20V');expect(ref,2,'BUS_20V')
    for i,net in enumerate(['BUS_20V','LOCAL_20V_RAW','TILE_20V','MODULE_20V'],4):
        expect('D'+str(i),1,net);expect('D'+str(i),2,'GND')
    for pin,net in enumerate(['BUS_20V','TILE_20V','+5V','+3V3','MODULE_5V','MODULE_20V','GND','RGB_DOUT_TEST'],1):expect('TP'+str(pin),1,net)
    for pin in [1,28]:disconnected('U1',pin)
    for ref,pins in [('U3',[3,10]),('U4',[4]),('U5',[10]),('U7',[7,10]),('U13',[11,12]),('U14',[4])]:
        for pin in pins:disconnected(ref,pin)
    # These boundaries must remain separate even if an ERC-clean accidental wire is introduced.
    for names in [('GND','LOCAL_RTN','MODULE_RTN'),('BUS_20V','LOCAL_20V_RAW','TILE_20V'),
                  ('BUS_SENSE','BUS_SENSE_RAW'),*(('MODULE_'+s,'MODULE_'+s+'_PAD') for s in ['SDA','SCL','CTRL','ID'])]:
        if len({frozenset(members[n]) for n in names}) != len(names):raise ValueError(f'Isolation boundary shorted: {names}')
        checks += 1
    components=root.findall('./components/comp')
    missing=[c.attrib['ref'] for c in components if not c.findtext('footprint') and not any(
        p.attrib['name']=='exclude_from_board' for p in c.findall('property'))]
    return checks,len(components),len(members),missing


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('netlist');args=parser.parse_args()
    try:checks,components,nets,missing=inspect(args.netlist)
    except (ValueError,KeyError) as e:raise SystemExit(str(e))
    print(f'PASS: {checks} connectivity checks; {components} components; {nets} nets.')
    print('Missing onboard footprints: '+', '.join(missing))
    print('Connectivity checks do not establish transient survival, Ioff performance, fuse coordination or mechanical qualification.')


if __name__=='__main__':main()
