#!/usr/bin/env python3
"""Native KiCad checks. Reports incomplete layout explicitly; never suppresses other DRC faults."""
import argparse
import collections
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent


def cli():
    if os.environ.get('KICAD_CLI'):return shlex.split(os.environ['KICAD_CLI'])
    if shutil.which('kicad-cli'):return ['kicad-cli']
    if shutil.which('flatpak'):return ['flatpak','run','--command=kicad-cli','org.kicad.KiCad']
    raise RuntimeError('Install KiCad CLI or set KICAD_CLI')


def export_netlists(output):
    for board in ('tile','hub'):
        subprocess.run(cli()+['sch','export','netlist','--format','kicadxml','--output',str(output/f'{board}.xml'),str(ROOT/f'hardware/electronics/{board}/{board}.kicad_sch')],check=True)


def verify(output):
    export_netlists(output)
    (output/'footprints').mkdir(exist_ok=True)
    subprocess.run(cli()+['fp','export','svg','--layers','F.Cu,F.Silkscreen,F.CrtYd','--output',str(output/'footprints'),str(ROOT/'hardware/electronics/libraries/Klink.pretty')],check=True)
    expected={p.stem for p in (ROOT/'hardware/electronics/libraries/Klink.pretty').glob('*.kicad_mod')}
    actual={p.stem for p in (output/'footprints').glob('*.svg')}
    if actual!=expected:raise RuntimeError(f'Native footprint exports missing: {expected-actual}')
    for board in ('tile','hub'):
        subprocess.run(cli()+['sch','erc','--format','json','--severity-all','--exit-code-violations','--output',str(output/f'{board}-erc.json'),str(ROOT/f'hardware/electronics/{board}/{board}.kicad_sch')],check=True)
        subprocess.run([sys.executable,'-B',str(HERE/f'check_{board}_netlist.py'),str(output/f'{board}.xml')],check=True)
    targets=[('tile','tile/tile.kicad_pcb',True),('spring','contact-test/spring-contact-test.kicad_pcb',False),('flat','contact-test/flat-contact-test.kicad_pcb',False)]
    for name,path,parity in targets:
        report=output/f'{name}-drc.json'
        result=subprocess.run(cli()+['pcb','drc','--format','json','--severity-all','--exit-code-violations']+(['--schematic-parity']if parity else [])+['--output',str(report),str(ROOT/'hardware/electronics'/path)])
        if result.returncode not in (0,5):raise RuntimeError(f'{name} DRC failed: {result.returncode}')
        data=json.loads(report.read_text())
        counts={key:dict(collections.Counter(x['type'] for x in data.get(key,[])))for key in ('violations','unconnected_items','schematic_parity')}
        print(name,counts,flush=True)
        allowed={'violations':{'invalid_outline'},'unconnected_items':{'unconnected_items'},'schematic_parity':{'missing_footprint'}} if parity else {key:set()for key in counts}
        for key,types in counts.items():
            if set(types)-allowed[key]:raise RuntimeError(f'Unexpected {name} {key}: {types}')
        if parity and counts['violations'].get('invalid_outline')!=1:raise RuntimeError('Review changed tile outline state')
    env=dict(os.environ,KLINK_NETLIST_DIR=str(output),PYTHONDONTWRITEBYTECODE='1')
    subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(HERE),'-p','test_engineering.py','-v'],check=True,env=env)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.output:
        a.output.mkdir(parents=True,exist_ok=True);verify(a.output.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='.klink-checks-',dir=Path.home())as directory:verify(Path(directory))
