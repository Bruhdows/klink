#!/usr/bin/env python3
"""Compare DC architectures; resistance targets are assumptions, not qualified contacts."""
import argparse
import csv
import json
import math
import sys
from power_budget import estimate,geometry,links
from hub_limits import limits

ARCHITECTURES={
    'rev_a_fused':dict(positive_r=.22,return_r=.07,fuse_r=.075),
    'low_r_same_fuses':dict(positive_r=.17,return_r=.02,fuse_r=.075),
    'no_edge_fuses_old_contacts':dict(positive_r=.07,return_r=.07,fuse_r=0),
    '80m_loop_target':dict(positive_r=.04,return_r=.04,fuse_r=0),
    '40m_loop_target':dict(positive_r=.02,return_r=.02,fuse_r=0),
}


def operating_point(architecture,count,position,watts,bus=19,**kwargs):
    return estimate(count,position,watts,local_r=.225,source_r=.12,bus=bus,
                    common_r=.12,hub_watts=5,**ARCHITECTURES[architecture],**kwargs)


def eligible(r,architecture,temperature=70):
    if r is None or r.get('status')!='DC_SOLVED':return False
    # F1 remains even when transit fuses are removed.
    fuse_budget=.75 if temperature<=25 else .6
    return (r['min_voltage']>=15.75 and r['local_current']<=fuse_budget
            and r['source_current']<=limits(125,limit_ohms=10000)['trip_min_A']
            and r['total_current']<=limits(125)['trip_min_A']
            and (not ARCHITECTURES[architecture]['fuse_r'] or r['positive_current']<=fuse_budget))


def envelope(architecture,count,position,bus=19,temperature=70):
    low,high=0.,14.
    for _ in range(24):
        mid=(low+high)/2;r=operating_point(architecture,count,position,mid,bus)
        if eligible(r,architecture,temperature):low=mid
        else:high=mid
    return low


def chain_diagnosis():
    n,p,v=20,3.,20.;minimum_i=p/v
    # Lower current bounds from Vtile <= Vsource; these are not a DC operating point.
    remaining=list(range(n-1,0,-1));branch=n*minimum_i
    positive_branch=.22-.075+.15
    copper_contact_loss=(branch*branch*(positive_branch-.075+.07)
                         +sum((m*minimum_i)**2*.14 for m in remaining))
    edge_fuse_loss=branch*branch*.075+sum((m*minimum_i)**2*.15 for m in remaining)
    local_loss=n*minimum_i**2*.225
    common_loss=(branch+5/v)**2*.1
    far_drop=branch*(positive_branch+.07)+sum(m*minimum_i*.29 for m in remaining)+minimum_i*.225+(branch+5/v)*.1
    failed=estimate(n,'chain',p,.22,.07,.225,.15,v,common_r=.1,hub_watts=5,details=True)
    low,high=0.,3.
    for _ in range(18):
        mid=(low+high)/2
        if estimate(n,'chain',mid,.22,.07,.225,.15,v,common_r=.1,hub_watts=5)is None:high=mid
        else:low=mid
    return dict(load_W=60,first_branch_minimum_A=branch,
                first_contact_minimum_loss_W=.05*branch**2,
                first_edge_fuse_minimum_loss_W=.075*branch**2,
                current_over_25C_fuse_budget=branch/.75,current_over_70C_fuse_budget=branch/.6,
                optimistic_far_end_drop_V=far_drop,optimistic_far_end_upper_bound_V=v-far_drop,
                loss_lower_bound_W=dict(contacts_copper_switch=copper_contact_loss,
                                       transit_fuses=edge_fuse_loss,local_paths=local_loss,common_input=common_loss),
                collapse_bound_iterations=failed['iterations'],failed_voltage_upper_bound_V=min(failed['failed_bound_V']),
                uniform_positive_DC_boundary_W_per_tile=[low,high])


def openings(architecture='80m_loop_target',count=20,position='corner',watts=3,bus=19):
    tiles,hub=geometry(count,position);edges,branches=links(tiles,hub)
    cases=[('edge',i,j)for i,j in edges]+[('branch',k)for k in range(len(branches))]
    rows=[]
    for path in cases:
        for mode in ('positive','return','connection'):
            r=operating_point(architecture,count,position,watts,bus,
                              opened=path if mode!='return'else None,
                              opened_return=path if mode!='positive'else None)
            rows.append(dict(path=path,mode=mode,solved=r is not None,
                             eligible=eligible(r,architecture),
                             min_V=None if r is None else r['min_voltage'],
                             positive_A=None if r is None else r['positive_current'],
                             return_A=None if r is None else r['return_current']))
    return rows


def copper(width_mm=4,thickness_um=35,layers=2,length_mm=80,temperature=70,current=5.0):
    rho=1.724e-8*(1+.00393*(temperature-20))
    area=width_mm*1e-3*thickness_um*1e-6*layers
    resistance=rho*length_mm*1e-3/area
    return dict(conductor_ohms=resistance,drop_V=current*resistance,loss_W=current*current*resistance,
                parallel_layers=layers)


def energy(cap_uF,volts=21,resistance=.04):
    # Source-free RC discharge. A very low contact resistance increases pulse current.
    c=cap_uF*1e-6
    return dict(energy_J=.5*c*volts**2,initial_A=volts/resistance,
                integral_A2s=c*volts**2/(2*resistance),time_constant_s=c*resistance)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--chain',action='store_true');p.add_argument('--openings',action='store_true');a=p.parse_args()
    if a.chain:print(json.dumps(chain_diagnosis(),indent=2))
    elif a.openings:
        for architecture in ('rev_a_fused','80m_loop_target','40m_loop_target'):
            for position in ('center','edge','corner'):
                rows=openings(architecture,position=position)
                solved=[r for r in rows if r['solved']]
                print(json.dumps(dict(architecture=architecture,topology=position,cases=len(rows),
                                     disconnected=sum(not r['solved']for r in rows),
                                     outside_limits=sum(not r['eligible']for r in rows),
                                     max_positive_A=max(r['positive_A']for r in solved),
                                     max_return_A=max(r['return_A']for r in solved),
                                     min_V=min(r['min_V']for r in solved))))
    else:
        writer=csv.writer(sys.stdout);writer.writerow(['architecture','tiles','topology','bus_V','W_per_tile','min_V','max_positive_A','max_return_A','source_A','loss_W','eligible_70C'])
        for architecture in ARCHITECTURES:
            for count in (16,20):
                for bus in (18.5,19,20):
                    for position in ('chain','center','edge','corner'):
                        r=operating_point(architecture,count,position,3,bus)
                        writer.writerow([architecture,count,position,bus,3]+(['']*5+[False]if r is None else [r['min_voltage'],r['positive_current'],r['return_current'],r['total_current'],r['loss_watts'],eligible(r,architecture)]))
