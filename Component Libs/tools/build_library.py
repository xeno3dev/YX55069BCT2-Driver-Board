"""One-time import builder. Sources are read-only; outputs stay in this repo.

python build_library.py --slate <slate113_libs> --kicad <share/kicad>
Normal use of the resulting library does NOT require these source installations.
"""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path
from sexpr import Quoted as Q, parse, dump, child, children, walk

ap = argparse.ArgumentParser()
ap.add_argument('--slate', type=Path, required=True)
ap.add_argument('--kicad', type=Path, required=True)
args = ap.parse_args()
base = Path(__file__).resolve().parents[1]
repo = base.parent
nickname = 'YX55069BCT2'
outfp = base / (nickname + '.pretty')
# This directory is generated solely by this script. Clean it to prevent a
# renamed/legacy EasyEDA footprint from surviving a subsequent rebuild.
if outfp.exists():
    shutil.rmtree(outfp)
outfp.mkdir()
symbols, manifest, cache = [], [], {}

def library(path):
    if path not in cache:
        cache[path] = {x[1]: x for x in children(parse(path.read_text(encoding='utf-8')), 'symbol')}
    return cache[path]

def resolved(path, name):
    node = copy.deepcopy(library(path)[name])
    extends = child(node, 'extends')
    if extends:
        parent = resolved(path, extends[1])
        old = parent[1]
        parent[1] = Q(name)
        for sub in children(parent, 'symbol'):
            sub[1] = Q(str(sub[1]).replace(old + '_', name + '_', 1))
        for prop in children(node, 'property'):
            parent[:] = [x for x in parent if not (isinstance(x, list) and x[:2] == prop[:2])]
            parent.append(prop)
        node = parent
    return node

def prop(node, key, value):
    target = next((x for x in children(node, 'property') if x[1] == key), None)
    if target:
        target[2] = Q(value)
    else:
        node.insert(2, ['property', Q(key), Q(value), ['at','0','0','0'], ['effects',['font',['size','1.27','1.27']],['hide','yes']]])

def fp_copy(path):
    node = parse(path.read_text(encoding='utf-8'))
    # No dangling machine-specific/stock-library 3D links. 2D footprint is complete.
    node[:] = [x for x in node if not (isinstance(x,list) and x and x[0] == 'model')]
    # Some Slate EasyEDA footprints carry a library alias in the footprint
    # name itself. A .pretty library must expose an unqualified basename.
    name = str(node[1]).rsplit(':', 1)[-1]
    node[1] = Q(name)
    (outfp / (name + '.kicad_mod')).write_text(dump(node) + '\n', encoding='utf-8')
    return nickname + ':' + name

def add(path, name, new=None, footprint=None, value=None, fields=None):
    node = resolved(path, name)
    new = new or name
    node[1] = Q(new)
    for sub in children(node,'symbol'):
        sub[1] = Q(str(sub[1]).replace(name + '_', new + '_', 1))
    if new != name or value:
        prop(node,'Value',value or new)
    oldfp = next((x[2] for x in children(node,'property') if x[1]=='Footprint'), '')
    if footprint:
        fppath = args.kicad / 'footprints' / (footprint.split(':')[0] + '.pretty') / (footprint.split(':')[1]+'.kicad_mod')
    elif oldfp:
        # Slate's EasyEDA imports carry a legacy three-section alias such as
        # slate113:easyeda2kicad:FPC-....  The final section is the real mod.
        lib = oldfp.split(':', 1)[0]
        fn = oldfp.rsplit(':', 1)[-1]
        fppath = (args.slate / 'slate113.pretty' if lib == 'slate113' else args.kicad / 'footprints' / (lib+'.pretty')) / (fn+'.kicad_mod')
        if lib.endswith('_import'):
            # Locally cached EasyEDA/LCSC imports are kept beside this builder
            # and copied into the portable .pretty output during a rebuild.
            fppath = base / 'sources' / (lib + '.pretty') / (fn+'.kicad_mod')
    else:
        fppath = None
    if fppath:
        prop(node,'Footprint',fp_copy(fppath))
    for k,v in (fields or {}).items():
        prop(node,k,v)
    # Historical EasyEDA IDs do not belong in current library syntax.
    for p in children(node,'property'):
        p[:] = [x for x in p if not (isinstance(x,list) and x and x[0]=='id')]
    symbols.append(node)
    manifest.append({'symbol':new,'source_library':path.name,'source_symbol':name,
                     'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'footprint':next((x[2] for x in children(node,'property') if x[1]=='Footprint'),'')})
    return node

slate = args.slate / 'slate113.kicad_sym'
exact = {
    'TYPE-C16PIN': {'MPN':'TYPE-C16PIN','Manufacturer':'Shou Han','LCSC':'C393939',
                    'Datasheet':'https://www.lcsc.com/product-detail/C393939.html'},
    'FPC0.5-24P': {'MPN':'F-FPC0M24P-C310','Manufacturer':'CKMTW','LCSC':'C132514',
                   'Datasheet':'https://www.lcsc.com/product-detail/C132514.html'},
    'FPC-0.5FX-6PWBH10': {'MPN':'FPC-0.5FX-6PWBH10','Manufacturer':'Xunpu','LCSC':'C5343255',
                          'Datasheet':'https://www.lcsc.com/product-detail/C5343255.html'},
    'PCA9306DCUR': {'MPN':'PCA9306DCUR','Manufacturer':'TI','LCSC':'C33196',
                    'Datasheet':'https://www.ti.com/product/PCA9306'},
    'AP2112K-3.3TRG1': {'MPN':'AP2112K-3.3TRG1','Manufacturer':'Diodes','LCSC':'C51118',
                        'Datasheet':'https://www.diodes.com/part/view/AP2112'},
    'AP2112K-1.8TRG1': {'MPN':'AP2112K-1.8TRG1','Manufacturer':'Diodes','LCSC':'C176944',
                        'Datasheet':'https://www.diodes.com/part/view/AP2112'},
    'AP2120N-2.8TRG1': {'MPN':'AP2120N-2.8TRG1','Manufacturer':'Diodes','LCSC':'C6500826',
                        'Datasheet':'https://www.diodes.com/datasheet/download/AP2120.pdf'},
    'LP8556SQ-E09_NOPB': {'MPN':'LP8556SQ-E09/NOPB','Manufacturer':'TI','LCSC':'C2679180',
                          'Datasheet':'https://www.ti.com/lit/ds/symlink/lp8556.pdf'},
}
for name, fields in exact.items():
    add(slate,name,fields={'Source':'Slate113 project library; imported without editing source', **fields})
add(args.kicad/'symbols/Regulator_Linear.kicad_sym','AP2112K-1.2',new='AP2112K-1.2TRG1',
    fields={'MPN':'AP2112K-1.2TRG1','Manufacturer':'Diodes','LCSC':'C460310',
            'Datasheet':'https://www.diodes.com/part/view/AP2112',
            'Role':'Dedicated 1.2 V TC358870 MIPI D-PHY rail; do not merge with 1.1 V rails.'})

esp = add(slate,'ESP32-S3-WROOM-1U-N8','ESP32-S3-WROOM-1-N16R8',
          footprint='RF_Module:ESP32-S3-WROOM-1',fields={
              'MPN':'ESP32-S3-WROOM-1-N16R8',
              'Manufacturer':'Espressif','LCSC':'C2913202',
              'LCSC Link':'https://www.lcsc.com/product-detail/C2913202.html',
              'Datasheet':'https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf',
              'Description':'16 MB flash, 8 MB octal PSRAM, PCB antenna. GPIO35/36/37 reserved for PSRAM; do not connect.',
              'Source':'Adapted Slate113 1U-N8 pinout; KiCad WROOM-1 PCB-antenna footprint'})
for p in children(esp,'property')[:]:
    if str(p[1]) in ['LCSC Part #','JLCPCB Part #','Supplier Part','Purchase Link']:
        esp.remove(p)
for p in walk(esp):
    if p and p[0]=='pin' and child(p,'number') and child(p,'number')[1] in ['28','29','30']:
        p[1]='no_connect'
        child(p,'name')[1]=Q('RESERVED_PSRAM')

add(slate, 'ESP32-S3-WROOM-1U-N8', fields={
    'MPN':'ESP32-S3-WROOM-1U-N8', 'Manufacturer':'Espressif', 'LCSC':'C2980297',
    'LCSC Link':'https://www.lcsc.com/product-detail/C2980297.html',
    'Datasheet':'https://www.lcsc.com/datasheet/C2980297.pdf',
    'Description':'8 MB flash, external antenna connector. Use the module datasheet for pin-use constraints.',
    'Source':'Slate113 EasyEDA/LCSC C2980297 import; external-antenna 1U footprint copied locally for portable project use'})

# ESP32-S3 bare-chip support parts.  These are intentionally source imports
# rather than generic KiCad symbols, so their supplier pin maps and land
# patterns remain traceable and reproducible.
for source, name, fields in [
    ('C2913194', 'ESP32-S3R8', {'MPN':'ESP32-S3R8', 'Manufacturer':'Espressif', 'LCSC':'C2913194',
        'LCSC Link':'https://www.lcsc.com/product-detail/C2913194.html',
        'Role':'Bare ESP32-S3 with 8 MB in-package octal PSRAM.'}),
    ('C2982923', 'GD25Q128EWIGR', {'MPN':'GD25Q128EWIGR', 'Manufacturer':'GigaDevice', 'LCSC':'C2982923',
        'LCSC Link':'https://www.lcsc.com/product-detail/C2982923.html',
        'Role':'16 MB, 3.3 V Quad-SPI NOR flash for ESP32-S3 external flash.'}),
    ('C1986736', 'ABM8-40.000MHZ-10-D1G-T', {'MPN':'ABM8-40.000MHZ-10-D1G-T', 'Manufacturer':'Abracon', 'LCSC':'C1986736',
        'LCSC Link':'https://www.lcsc.com/product-detail/C1986736.html',
        'Role':'40 MHz, 10 pF-load crystal for ESP32-S3.'}),
    ('C86285', 'CL05C150JB5NNNC', {'MPN':'CL05C150JB5NNNC', 'Manufacturer':'Samsung Electro-Mechanics', 'LCSC':'C86285',
        'LCSC Link':'https://www.lcsc.com/product-detail/C86285.html',
        'Value':'15 pF', 'Dielectric':'C0G', 'Voltage':'50 V'}),
    ('C77044', 'GRM188R61A106KE69D', {'MPN':'GRM188R61A106KE69D', 'Manufacturer':'Murata', 'LCSC':'C77044',
        'LCSC Link':'https://www.lcsc.com/product-detail/C77044.html',
        'Value':'10 uF', 'Dielectric':'X5R', 'Voltage':'10 V'}),
    ('C52923', 'CL05A105KA5NQNC', {'MPN':'CL05A105KA5NQNC', 'Manufacturer':'Samsung Electro-Mechanics', 'LCSC':'C52923',
        'LCSC Link':'https://www.lcsc.com/product-detail/C52923.html',
        'Value':'1 uF', 'Dielectric':'X5R', 'Voltage':'25 V'}),
    ('C1525', 'CL05B104KO5NNNC', {'MPN':'CL05B104KO5NNNC', 'Manufacturer':'Samsung Electro-Mechanics', 'LCSC':'C1525',
        'LCSC Link':'https://www.lcsc.com/product-detail/C1525.html',
        'Value':'100 nF', 'Dielectric':'X7R', 'Voltage':'16 V'}),
    ('C71633', 'GRM188R61A475KE15D', {'MPN':'GRM188R61A475KE15D', 'Manufacturer':'Murata', 'LCSC':'C71633',
        'LCSC Link':'https://www.lcsc.com/product-detail/C71633.html',
        'Value':'4.7 uF', 'Dielectric':'X5R', 'Voltage':'10 V'}),
    ('C60490', 'RC0402FR-0710KL', {'MPN':'RC0402FR-0710KL', 'Manufacturer':'Yageo', 'LCSC':'C60490',
        'LCSC Link':'https://www.lcsc.com/product-detail/C60490.html', 'Value':'10 kOhm', 'Tolerance':'1%'}),
    ('C60488', 'RC0402FR-072KL', {'MPN':'RC0402FR-072KL', 'Manufacturer':'Yageo', 'LCSC':'C60488',
        'LCSC Link':'https://www.lcsc.com/product-detail/C60488.html', 'Value':'2.00 kOhm', 'Tolerance':'1%'}),
    ('C114765', 'RC0402FR-0722RL', {'MPN':'RC0402FR-0722RL', 'Manufacturer':'Yageo', 'LCSC':'C114765',
        'LCSC Link':'https://www.lcsc.com/product-detail/C114765.html', 'Value':'22 Ohm', 'Tolerance':'1%'}),
    ('C106231', 'RC0402FR-070RL', {'MPN':'RC0402FR-070RL', 'Manufacturer':'Yageo', 'LCSC':'C106231',
        'LCSC Link':'https://www.lcsc.com/product-detail/C106231.html', 'Value':'0 Ohm', 'Tolerance':'1%'}),
    ('C106232', 'RC0402FR-07100RL', {'MPN':'RC0402FR-07100RL', 'Manufacturer':'Yageo', 'LCSC':'C106232',
        'LCSC Link':'https://www.lcsc.com/product-detail/C106232.html', 'Value':'100 Ohm', 'Tolerance':'1%'}),
    ('C137970', 'RC0402FR-07499RL', {'MPN':'RC0402FR-07499RL', 'Manufacturer':'Yageo', 'LCSC':'C137970',
        'LCSC Link':'https://www.lcsc.com/product-detail/C137970.html', 'Value':'499 Ohm', 'Tolerance':'1%'}),
    ('C138021', 'RC0402FR-0727RL', {'MPN':'RC0402FR-0727RL', 'Manufacturer':'Yageo', 'LCSC':'C138021',
        'LCSC Link':'https://www.lcsc.com/product-detail/C138021.html', 'Value':'27 Ohm', 'Tolerance':'1%'}),
]:
    add(base/'sources'/(source + '_import.kicad_sym'),
        'ESP32-S3' if source == 'C2913194' else name, new=name, fields={
        **fields, 'Source':f'EasyEDA/LCSC {source} import; footprint copied locally for portable project use'})

add(base/'sources/C142185_import.kicad_sym', 'CS0402-24NJ-S', fields={
    'MPN':'CS0402-24NJ-S', 'Manufacturer':'Chilisin', 'LCSC':'C142185',
    'LCSC Link':'https://www.lcsc.com/product-detail/C142185.html',
    'Value':'24 nH', 'Package':'0402', 'Tolerance':'5%', 'Current Rating':'400 mA', 'DCR':'300 mOhm',
    'Substitutes':'LQG15HS24NJ02D (no usable LCSC listing)',
    'Source':'EasyEDA/LCSC C142185 import; in-stock exact-inductance replacement for LQG15HS24NJ02D'})

add(base/'sources/C405304_import.kicad_sym', 'S16', fields={
    'MPN':'S16', 'Manufacturer':'Yangjie', 'LCSC':'C405304',
    'LCSC Link':'https://www.lcsc.com/product-detail/C405304.html',
    'Source':'EasyEDA/LCSC C405304 import; footprint copied locally for portable project use'})

add(base/'sources/C2677392_import.kicad_sym', 'SN74AXC1T45DCKR', fields={
    'MPN':'SN74AXC1T45DCKR', 'Manufacturer':'Texas Instruments', 'LCSC':'C2677392',
    'LCSC Link':'https://www.lcsc.com/product-detail/C2677392.html',
    'Role':'Single-bit bidirectional dual-supply level translator; DIR selects the A-to-B direction.',
    'Source':'EasyEDA/LCSC C2677392 import; footprint copied locally for portable project use'})

bridge=add(base/'sources/tc358870_import.kicad_sym','TC358870XBG','TC358870XBG(NOK)',fields={
    'MPN':'TC358870XBG(NOK)','LCSC':'C3008712',
    'Datasheet':'https://www.lcsc.com/datasheet/C3008712.pdf',
    'Description':'HDMI RX to dual 4-lane MIPI DSI TX; up to 1 Gbit/s/lane. Host register initialization required; no assumed panel compatibility.',
    'Source':'EasyEDA/LCSC C3008712 import; pin-map validation in validation report'})

add(base/'sources/C2678061_import.kicad_sym','STUSB4500QTR',fields={
    'MPN':'STUSB4500QTR','Manufacturer':'STMicroelectronics','LCSC':'C2678061',
    'LCSC Link':'https://www.lcsc.com/product-detail/C2678061.html',
    'Datasheet':'https://www.st.com/resource/en/datasheet/stusb4500.pdf',
    'Role':'Optional USB-C Power Delivery sink controller with integrated CC attach/detach handling. It does not implement DisplayPort Alt Mode.',
    'Source':'EasyEDA/LCSC C2678061 import; footprint copied locally for portable project use'})

add(base/'sources/C2838439_import.kicad_sym','SED5120',fields={
    'MPN':'SED5120','Manufacturer':'Seaward Elec','LCSC':'C2838439',
    'LCSC Link':'https://www.lcsc.com/product-detail/C2838439.html',
    'Datasheet':'https://lcsc.com/datasheet/lcsc_datasheet_2410121612_Seaward-Elec-SED5120_C2838439.pdf',
    'Role':'Nominal 3.3 V SOT-223 LDO option. Check dissipation at the chosen input voltage and meet its specified output-capacitor requirement.',
    'Source':'EasyEDA/LCSC C2838439 import; footprint copied locally for portable project use'})

add(base/'sources/OT7EL89CJI-111YLC-48M_import.kicad_sym', 'OT7EL89CJI-111YLC-48M', fields={
    'MPN':'OT7EL89CJI-111YLC-48M', 'Manufacturer':'YXC(扬兴晶振)', 'LCSC':'C7434946',
    'LCSC Link':'https://www.lcsc.com/product-detail/C7434946.html',
    'Datasheet':'https://www.lcsc.com/datasheet/C7434946.pdf',
    'Frequency':'48 MHz', 'Supply Voltage':'1.8–3.3 V', 'Output Type':'CMOS',
    'Role':'48 MHz CMOS oscillator for a 1.8 V supply; pin 1 tri-state/OE, pin 2 GND, pin 3 OUT, pin 4 VDD.',
    'Source':'EasyEDA/LCSC C7434946 import; footprint copied locally for portable project use'})

add(base/'sources/C112239_import.kicad_sym', 'BSS138_C112239', fields={
    'MPN':'BSS138', 'Manufacturer':'SHIKUES(时科)', 'LCSC':'C112239',
    'LCSC Link':'https://www.lcsc.com/product-detail/C112239.html',
    'Datasheet':'https://lcsc.com/product-detail/MOSFET_BSS138_C112239.html',
    'Source':'EasyEDA/LCSC C112239 import; footprint copied locally for portable project use'})

for name, lcsc, voltage in [
    ('TLV76733DRVR', 'C2848334', '3.3 V'),
    ('TLV76728DRVR', 'C2865665', '2.8 V'),
    ('TLV76718DRVR', 'C2870458', '1.8 V'),
    ('TLV76701DRVR', 'C2863998', '1.0 V'),
]:
    add(base/'sources/TLV767_import.kicad_sym', name, fields={
        'MPN':name, 'LCSC':lcsc,
        'LCSC Link':f'https://www.lcsc.com/product-detail/{lcsc}.html',
        'Output Voltage':voltage,
        'Source':f'EasyEDA/LCSC {lcsc} import; footprint copied locally for portable project use'})

def stock(lib,name,**kwargs):
    return add(args.kicad/'symbols'/(lib+'.kicad_sym'),name,**kwargs)

stock('Connector','HDMI_A',new='10029449-001RLF',footprint='Connector_Video:HDMI_A_Amphenol_10029449-x01xLF_Horizontal',fields={
    'MPN':'10029449-001RLF','Manufacturer':'Amphenol','LCSC':'C428493','LCSC Link':'https://www.lcsc.com/product-detail/C428493.html',
    'Datasheet':'https://cdn.amphenol-icc.com/media/wysiwyg/files/drawing/10029449.pdf'})
stock('Power_Protection','USBLC6-2SC6',fields={'MPN':'USBLC6-2SC6','Manufacturer':'STMicroelectronics','LCSC':'C7519',
    'LCSC Link':'https://www.lcsc.com/product-detail/C7519.html','Datasheet':'https://www.st.com/resource/en/datasheet/usblc6-2.pdf'})
stock('Regulator_Switching','TPS62160DGK',new='TPS62160DGKR',fields={'MPN':'TPS62160DGKR','Role':'Adjustable 1.1/1.2 V bridge rails or efficient 3.3 V supply; use separate converter per rail'})
stock('Logic_LevelTranslator','SN74LVC1T45DBV',new='SN74LVC1T45DBVR',fields={'MPN':'SN74LVC1T45DBVR','Role':'Direction-controlled translation of RESET/INT; DIR referenced to VCCA'})
stock('Power_Protection','TPD4E05U06DQA',new='TPD4E05U06DQAR',fields={'MPN':'TPD4E05U06DQAR','Role':'Low-capacitance ESD for HDMI TMDS; use two for all eight conductors'})
stock('Power_Management','TPS22917DBV',new='TPS22917DBVR',fields={'MPN':'TPS22917DBVR','Role':'Optional controlled panel power/load switch; current budget still required'})
stock('Transistor_FET','2N7002',fields={'Role':'Open-drain reset, enable and optional level translation'})
stock('Device','D_Schottky',new='SS16',footprint='Diode_SMD:D_SMA',value='SS16 1A 60V',fields={'MPN':'SS16','Role':'Backlight boost rectifier candidate; check peak/RMS current and thermal margin'})
for val in ['0','22','33','100','1k','2k','4.7k','5.1k','10k','24.9k','37.4k','49.9k','100k','200k','301k']:
    stock('Device','R',new='R_'+val+'_0603',footprint='Resistor_SMD:R_0603_1608Metric',value=val,fields={'Tolerance':'1%','Role':'5.1k: separate CC1/CC2 Rd; 200k: PCA9306 bias; others support/strap/feedback'})
for val,voltage,package in [('10nF','25V','0603'),('100nF','25V','0603'),('1uF','16V','0603'),('2.2uF','16V','0603'),('4.7uF','16V','0805'),('10uF','16V','0805'),('22uF','10V','0805'),('4.7uF','50V','1206'),('1uF','50V','1206')]:
    metric={'0603':'1608','0805':'2012','1206':'3216'}[package]
    stock('Device','C',new=f'C_{val}_{voltage}_{package}',footprint=f'Capacitor_SMD:C_{package}_{metric}Metric',value=val,fields={'Voltage':voltage,'Dielectric':'X7R or X5R; verify effective capacitance under DC bias'})
stock('Device','L',new='L_2.2uH_Buck',footprint='Inductor_SMD:L_Taiyo-Yuden_MD-3030',value='2.2uH',fields={'Role':'Buck inductor candidate; select MPN and Isat against TPS62160 peak current'})
stock('Device','L',new='L_Backlight_Select',footprint='Inductor_SMD:L_Taiyo-Yuden_MD-3030',value='SELECT_PANEL_LOAD',fields={'Role':'Footprint candidate only. Select inductance, package and Isat from LP8556 design equations and panel load'})
stock('Device','FerriteBead',new='Ferrite_Bead_0603',footprint='Inductor_SMD:L_0603_1608Metric',fields={'Role':'Optional rail filtering; impedance/current/DCR TBD'})
stock('Switch','SW_Push',new='SW_Reset_Boot',footprint='Button_Switch_SMD:SW_SPST_TL3342',fields={'Role':'Momentary reset or GPIO0 boot button; choose matching TL3342 switch'})
stock('Connector_Generic','Conn_01x06',new='Header_UART_Programming',footprint='Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical',fields={'Role':'GND/3V3/TX/RX/EN/BOOT; assign net order explicitly'})
stock('Connector_Generic','Conn_01x02',new='Header_5V_Input',footprint='Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
stock('Connector','TestPoint',footprint='TestPoint:TestPoint_Pad_D1.0mm')
stock('Device','Fuse',new='Fuse_1206',footprint='Fuse:Fuse_1206_3216Metric',fields={'Role':'Input fuse candidate; choose rating after power budget'})
stock('Device','LED',new='LED_0603',footprint='LED_SMD:LED_0603_1608Metric')
stock('Oscillator','ASE-xxxMHz',new='Oscillator_48MHz_1V8',footprint='Oscillator:Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm',value='48MHz 1.8V SELECT_MPN',fields={'Role':'1.8 V CMOS clock for TC358870 REFCLK; select 40-50 MHz per timing requirements, pin1 OE,2 GND,3 OUT,4 VDD'})
for name in ['GND','+1V1','+1V2','+1V8','+2V8','+3V3','+5V','PWR_FLAG']:
    stock('power',name)

root=['kicad_symbol_lib',['version','20231120'],['generator','kicad_symbol_editor']]+symbols
(base/(nickname+'.kicad_sym')).write_text(dump(root)+'\n',encoding='utf-8')
(base/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
for table,typ,ext in [('sym-lib-table','sym','kicad_sym'),('fp-lib-table','fp','pretty')]:
    p=repo/'Kicad Project'/table
    root=parse(p.read_text(encoding='utf-8')) if p.exists() else [typ+'_lib_table',['version','7']]
    entry = ['lib',['name',Q(nickname)],['type',Q('KiCad')],['uri',Q('${KIPRJMOD}/../Component Libs/'+nickname+'.'+ext)],['options',Q('')],['descr',Q('Portable YX55069BCT2 driver-board library')]]
    existing = next((x for x in children(root,'lib') if x[1][1] == nickname), None)
    if existing:
        root[root.index(existing)] = entry
    else:
        root.append(entry)
    p.write_text(dump(root)+'\n',encoding='utf-8')
print(f'Built {len(symbols)} symbols and {len(list(outfp.glob("*.kicad_mod")))} footprints')
