#!/usr/bin/env python3
"""DC estimates with separate positive/return meshes. Hardware limits are checked, not simulated here."""
import argparse
import csv
import math
import sys
from functools import lru_cache


def solve(matrix, rhs):
    a = [row[:] + [b] for row, b in zip(matrix, rhs)]
    n = len(a)
    for i in range(n):
        pivot = max(range(i, n), key=lambda k: abs(a[k][i]))
        a[i], a[pivot] = a[pivot], a[i]
        if abs(a[i][i]) < 1e-12:
            raise ValueError("Disconnected network")
        for j in range(i + 1, n):
            factor = a[j][i] / a[i][i]
            if not factor:
                continue
            for k in range(i + 1, n + 1):
                a[j][k] -= factor * a[i][k]
            a[j][i] = 0
    out = [0.] * n
    for i in range(n - 1, -1, -1):
        out[i] = (a[i][n] - sum(a[i][j] * out[j] for j in range(i + 1, n))) / a[i][i]
    return out


def geometry(count, position):
    if position == "chain":
        return [(x, 0) for x in range(1, count + 1)], {(0, 0)}
    width, height = {16:(6,3),20:(6,4),64:(11,6)}[count]
    x, y = ((2, 1) if count in (16,20) else (4, 2)) if position == "center" else (
        (width // 2 - 1, 0) if position == "edge" else (0, 0))
    hub = {(x, y), (x + 1, y)}
    tiles = [(i, j) for j in range(height) for i in range(width) if (i, j) not in hub]
    if count == 20:
        tiles = [p for p in tiles if p not in {(4, 3), (5, 3)}]
    if len(tiles) != count:
        raise ValueError("Geometry does not contain the requested tile count")
    return tiles, hub


def links(tiles, hub):
    index = {p: i for i, p in enumerate(tiles)}
    edges, branches = [], []
    for p, i in index.items():
        x, y = p
        for q in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
            if q in hub:
                branches.append(i)
            elif q in index and i < index[q]:
                edges.append((i, index[q]))
    return edges, branches


def conductance(count, edges, branches, edge_r, branch_r):
    matrix = [[0.] * count for _ in range(count)]
    for i, j in edges:
        g = 1 / edge_r
        matrix[i][i] += g
        matrix[j][j] += g
        matrix[i][j] -= g
        matrix[j][i] -= g
    for i in branches:
        matrix[i][i] += 1 / branch_r
    return matrix


@lru_cache(maxsize=32)
def impedance(count, edges, branches, positive_r, branch_r, return_r, local_r, common_r=0., ground_edges=None, ground_branches=None):
    """Terminal impedance including separate positive, return and local paths."""
    kp = conductance(count, edges, branches, positive_r, branch_r)
    kg = conductance(count, ground_edges if ground_edges is not None else edges,
                     ground_branches if ground_branches is not None else branches, return_r, return_r)
    z = [[0.] * count for _ in range(count)]
    for j in range(count):
        rhs = [float(i == j) for i in range(count)]
        p, g = solve(kp, rhs), solve(kg, rhs)
        for i in range(count):
            z[i][j] = p[i] + g[i] + (local_r if i == j else 0.) + common_r
            if z[i][j] < -1e-10:
                raise ArithmeticError('Passive-mesh impedance is not nonnegative')
    return z


def estimate(count, position, watts, positive_r, return_r, local_r, source_r, bus, fuse_r=0.075, common_r=0., hub_watts=0., opened=None, opened_return=None, details=False):
    tiles, hub = geometry(count, position)
    edges, branches = links(tiles, hub)
    loads = [float(watts)]*count if isinstance(watts,(int,float)) else list(watts)
    if len(loads)!=count or any(not math.isfinite(w) or w<0 for w in loads):
        raise ValueError('One finite nonnegative load is required per tile')
    op,og=opened_paths(opened),opened_paths(opened_return)
    ground_edges=[(i,j)for i,j in edges if ('edge',i,j)not in og]
    ground_branches=[i for k,i in enumerate(branches)if ('branch',k)not in og]
    edges=[(i,j)for i,j in edges if ('edge',i,j)not in op]
    branches=[i for k,i in enumerate(branches)if ('branch',k)not in op]
    # A tile-to-tile positive link has two tile fuses. The Hub branch has one tile fuse
    # and its own source-switch resistance, rather than a second tile's fuse.
    branch_positive_r = positive_r - fuse_r + source_r
    if branch_positive_r <= 0:
        raise ValueError("Invalid positive branch resistance")
    kp = conductance(count, edges, branches, positive_r, branch_positive_r)
    kg = conductance(count, ground_edges, ground_branches, return_r, return_r)
    try:
        z = impedance(count, tuple(edges), tuple(branches), positive_r,
                      branch_positive_r, return_r, local_r, common_r,
                      tuple(ground_edges),tuple(ground_branches))
    except ValueError as error:
        if str(error)!='Disconnected network':raise
        return dict(status='DISCONNECTED_ALL_LOADS_ON') if details else None
    # Every solution lies below bus. This monotone map tightens that upper bound.
    # A nonpositive bound rules out an all-loads-on positive DC operating point.
    protected = [bus] * count
    hub_voltage = bus
    for iteration in range(10000):
        current = [w / voltage for w,voltage in zip(loads,protected)]
        hub_current = hub_watts/hub_voltage
        new = [bus - sum(z[i][j] * current[j] for j in range(count)) - common_r*hub_current
               for i in range(count)]
        new_hub_voltage = bus-common_r*(sum(current)+hub_current)
        if min(new) <= 0 or new_hub_voltage <= 0:
            return dict(status='NO_POSITIVE_ALL_LOADS_ON_DC_SOLUTION',iterations=iteration+1,
                        previous_bound_V=protected,failed_bound_V=new,minimum_current_A=current) if details else None
        delta = max(max(abs(a-b) for a,b in zip(new, protected)),abs(new_hub_voltage-hub_voltage))
        protected = new
        hub_voltage = new_hub_voltage
        if delta < 1e-10:
            break
    else:
        raise ArithmeticError('Load-flow bounds did not converge; no collapse claim is justified')
    current = [w / voltage for w,voltage in zip(loads,protected)]
    hub_current = hub_watts/hub_voltage
    hub_voltage = bus - (sum(current)+hub_current)*common_r
    supply = [0.] * count
    for i in branches:supply[i] += hub_voltage/branch_positive_r
    vp = solve(kp, [b-i for b,i in zip(supply,current)])
    vg = solve(kg,current)
    protected = [p-g-i*local_r for p, g, i in zip(vp, vg, current)]
    branch_i = [(hub_voltage-vp[i])/branch_positive_r for i in branches]
    branch_g = [vg[i]/return_r for i in ground_branches]
    positive_i = [abs(vp[i]-vp[j])/positive_r for i, j in edges]
    return_i = [abs(vg[i]-vg[j])/return_r for i, j in ground_edges]
    loss = (sum(i*i*positive_r for i in positive_i) + sum(i*i*return_r for i in return_i)
            + sum(i*i*branch_positive_r for i in branch_i) + sum(i*i*return_r for i in branch_g)
            + sum(i*i*local_r for i in current))
    loss += common_r*(sum(branch_i)+hub_current)**2
    total = bus*(sum(branch_i)+hub_current)-hub_watts
    residual = abs(total-sum(loads)-loss)
    if residual > 0.001:
        raise ArithmeticError(f"Power balance residual {residual} W")
    return dict(status='DC_SOLVED',node_voltages=protected,node_currents=current,
                positive_currents=positive_i,return_currents=return_i,branch_currents=branch_i,
                ground_branch_currents=branch_g,loads=loads,
                iterations=iteration+1, min_voltage=min(protected), positive_current=max(branch_i+positive_i),
                return_current=max(branch_g+return_i), source_current=max(branch_i),
                local_current=max(current), total_current=sum(branch_i)+hub_current, input_watts=total, hub_voltage=hub_voltage,
                loss_watts=loss, energy_residual=residual, branches=len(branches))


def opened_paths(paths):
    if paths is None:return set()
    if isinstance(paths, tuple) and isinstance(paths[0], str):return {paths}
    return set(paths)


def fault_snapshot(count, position, fault_node, opened=None, bus=20., branch_limit=1.5, total_limit=4.5,
                   positive_r=0.22, return_r=0.07, source_r=0.15, short_r=0.01, fuse_r=0.075, opened_return=None, positive_overrides=None, return_overrides=None, common_r=0.):
    """Resistive snapshot with assumed ideal Hub limits. No fuse timing, capacitance or normal loads."""
    tiles, hub = geometry(count, position)
    edges, branches = links(tiles, hub)
    branch_r = positive_r - fuse_r + source_r
    if min(branch_r, positive_r, return_r, short_r, branch_limit, total_limit) <= 0:
        raise ValueError('Fault resistances and assumed limits must be positive')

    opened_positive = opened_paths(opened)
    opened_ground = opened_paths(opened_return)
    positive_overrides = positive_overrides or {}
    return_overrides = return_overrides or {}
    if any(not math.isfinite(r) or r <= 0 for r in
           list(positive_overrides.values()) + list(return_overrides.values())):
        raise ValueError('Individual path resistances must be finite and positive')
    def rp(i,j):return positive_overrides.get(('edge',i,j),positive_r)
    def rg(i,j):return return_overrides.get(('edge',i,j),return_r)
    def rb(k):return positive_overrides.get(('branch',k),branch_r)
    def rgb(k):return return_overrides.get(('branch',k),return_r)

    def at_voltage(voltage):
        capped = set()
        for _ in range(40):
            a = [[0.]*(2*count) for _ in range(2*count)]
            rhs = [0.]*(2*count)

            def connect(i,j,resistance):
                g=1/resistance
                a[i][i]+=g; a[j][j]+=g; a[i][j]-=g; a[j][i]-=g

            for i,j in edges:
                if ('edge',i,j) not in opened_positive:connect(i,j,rp(i,j))
                if ('edge',i,j) not in opened_ground:connect(i+count,j+count,rg(i,j))
            for k,i in enumerate(branches):
                # Ground stays connected when a positive fuse opens.
                if ('branch',k) not in opened_ground:a[i+count][i+count]+=1/rgb(k)
                if ('branch',k) in opened_positive:continue
                if k in capped:rhs[i]+=branch_limit
                else:
                    a[i][i]+=1/rb(k)
                    rhs[i]+=voltage/rb(k)
            connect(fault_node,fault_node+count,short_r)
            v=solve(a,rhs)
            new=set()
            for k,i in enumerate(branches):
                if ('branch',k) in opened_positive:continue
                if k in capped:
                    if v[i]+branch_limit*rb(k) <= voltage+1e-8:new.add(k)
                elif (voltage-v[i])/rb(k) > branch_limit+1e-8:new.add(k)
            if new==capped:break
            capped=new
        else:raise ArithmeticError('Fault branch-limit iteration did not converge')
        currents=[0 if ('branch',k) in opened_positive else branch_limit if k in capped else
                  (voltage-v[i])/rb(k) for k,i in enumerate(branches)]
        return v,currents

    v,currents=at_voltage(bus)
    source_voltage=bus
    if sum(currents)>total_limit or common_r:
        low,high=0.,bus
        for _ in range(26):
            mid=(low+high)/2
            trial,amps=at_voltage(mid)
            if sum(amps)>total_limit or mid+sum(amps)*common_r>bus:high=mid
            else:low=mid
        source_voltage=low
        v,currents=at_voltage(low)
    positive=[(abs(v[i]-v[j])/rp(i,j),('edge',i,j)) for i,j in edges if ('edge',i,j) not in opened_positive]
    positive += [(abs(current),('branch',k)) for k,current in enumerate(currents)]
    returns=[abs(v[i+count]-v[j+count])/rg(i,j) for i,j in edges if ('edge',i,j) not in opened_ground]
    returns += [v[i+count]/rgb(k) for k,i in enumerate(branches) if ('branch',k) not in opened_ground]
    incoming=[]
    for i,j in edges:
        key=('edge',i,j)
        if fault_node in (i,j) and key not in opened_positive:
            other=j if i==fault_node else i
            incoming.append(((v[other]-v[fault_node])/rp(i,j),key))
    incoming += [(currents[k],('branch',k)) for k,i in enumerate(branches) if i==fault_node and ('branch',k) not in opened_positive]
    return dict(max_positive=max(x[0] for x in positive),max_return=max(returns),total=sum(currents),
                source_voltage=source_voltage,short_current=(v[fault_node]-v[fault_node+count])/short_r,
                next_open=max(incoming)[1] if incoming else None)


def write_faults(args):
    writer=csv.writer(sys.stdout)
    writer.writerow(['tiles','topology','state','fault_xy','opened_positive_path','hub_total_A',
                     'hub_limit_voltage_V','short_A','max_positive_A','max_return_A','status'])
    rp=args.contact_ohms+args.copper_ohms+2*args.fuse_ohms
    rg=args.contact_ohms+args.copper_ohms
    for count in (20,64):
        for position in ('center','edge','corner'):
            tiles,hub=geometry(count,position)
            edges,branches=links(tiles,hub)
            selected=branches[0]
            nodes=range(count) if args.fault_sweep else [selected]
            settings=dict(positive_r=rp,return_r=rg,source_r=args.source_ohms,bus=args.bus_volts,
                          branch_limit=args.branch_limit_amps,total_limit=args.total_limit_amps,
                          fuse_r=args.fuse_ohms,common_r=args.common_ohms)
            for node in nodes:
                first=fault_snapshot(count,position,node,**settings)
                cases=[('all_fuses_closed',None,None,{}),('one_positive_fuse_open',first['next_open'],None,{})]
                if args.fault_sweep and count==20 and node==selected:
                    cases += [('one_return_open',None,key,{})for key in
                              [('edge',i,j)for i,j in edges]+[('branch',k)for k in range(len(branches))]]
                    cases += [('one_high_resistance_return',None,None,{'return_overrides':{('branch',k):10*rg}})
                              for k in range(len(branches))]
                    cases += [('all_hub_branches_off',{('branch',k)for k in range(len(branches))},None,{})]
                    if first['next_open'][0]=='edge':
                        cases += [('positive_and_return_open',first['next_open'],('branch',0),{})]
                for state,opened,ground,extra in cases:
                    try:
                        r=fault_snapshot(count,position,node,opened=opened,opened_return=ground,**extra,**settings)
                    except ValueError as error:
                        if str(error)!='Disconnected network':raise
                        writer.writerow([count,position,state,str(tiles[node]),repr((opened,ground,extra))]+['']*5+['DISCONNECTED_NETWORK_NO_DC_SNAPSHOT'])
                        continue
                    flags=['SNAPSHOT_ONLY_NO_CLEARING_TIME','CONTACT_CURRENT_UNQUALIFIED']
                    if r['max_positive']>1:flags.append('ABOVE_POSITIVE_FUSE_RATING')
                    if args.contact_screen_amps and r['max_return']>args.contact_screen_amps:flags.append('ABOVE_ASSUMED_CONTACT_SCREEN')
                    writer.writerow([count,position,state,str(tiles[node]),repr((opened,ground,extra)),
                                     f'{r["total"]:.6f}',f'{r["source_voltage"]:.6f}',f'{r["short_current"]:.6f}',
                                     f'{r["max_positive"]:.6f}',f'{r["max_return"]:.6f}','+'.join(flags)])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fault-sweep', action='store_true', help='With --faults, sweep every grid fault node and selected open/unequal-return cases')
    p.add_argument('--envelope', action='store_true', help='Bisect per-tile DC load at the requested fuse/source budgets; not qualification')
    p.add_argument('--faults', action='store_true', help='Write 12 current-limited resistive fault snapshots instead of 32 load cases')
    p.add_argument('--fuse-ohms', type=float, default=0.075, help='Each edge fuse; nominal cold value, not hot resistance')
    p.add_argument('--branch-limit-amps', type=float, default=1.5, help='Ideal held-current bound for reference snapshots; no latch timing')
    p.add_argument('--total-limit-amps', type=float, default=4.5, help='Ideal held-current bound for reference snapshots; no latch timing')
    p.add_argument('--contact-screen-amps', type=float, default=0, help='Optional numerical screen only; zero means no qualified contact limit')
    p.add_argument('--contact-ohms', type=float, default=0.05, help='Assumption per individual contact')
    p.add_argument('--copper-ohms', type=float, default=0.02, help='Assumption per conductor/link')
    p.add_argument('--local-ohms', type=float, default=0.225, help='F1 cold 0.075 plus U7 typical 0.15')
    p.add_argument('--common-ohms', type=float, default=0., help='Common Hub input path; separate from branch resistance')
    p.add_argument('--source-ohms', type=float, default=0.15, help='Assumed Hub branch switch resistance')
    p.add_argument('--bus-volts', type=float, default=20.)
    p.add_argument('--hub-watts', type=float, default=5.)
    p.add_argument('--fuse-continuous-amps', type=float, default=0.75, help='25C manufacturer rerating; use 0.60 at 70C')
    args = p.parse_args()
    if any(not math.isfinite(v) or v < 0 for v in vars(args).values()) or min(
            args.contact_ohms, args.bus_volts, args.fuse_continuous_amps, args.branch_limit_amps, args.total_limit_amps) == 0:
        p.error('Inputs must be finite and nonnegative; contact resistance, voltage and fuse budget must be positive')
    if args.fault_sweep and not args.faults:p.error('--fault-sweep requires --faults')
    if args.envelope and args.faults:p.error('Choose either --envelope or --faults')
    if args.envelope:
        writer=csv.writer(sys.stdout)
        writer.writerow(['tiles','topology','max_W_per_tile','limiting_positive_A','min_V','hub_input_W'])
        rp=args.contact_ohms+args.copper_ohms+2*args.fuse_ohms
        rg=args.contact_ohms+args.copper_ohms
        for count in (20,64):
            for topology in ('chain','center','edge','corner'):
                low,high=0.,14.
                for _ in range(30):
                    mid=(low+high)/2
                    r=estimate(count,topology,mid,rp,rg,args.local_ohms,args.source_ohms,args.bus_volts,args.fuse_ohms,args.common_ohms,args.hub_watts)
                    acceptable=r is not None and r['min_voltage']>=15.75 and max(r['positive_current'],r['local_current'])<=args.fuse_continuous_amps and r['local_current']<=.95/1.01 and r['source_current']<=args.branch_limit_amps and r['input_watts']+args.hub_watts<=min(100,args.bus_volts*args.total_limit_amps)
                    if acceptable:low=mid
                    else:high=mid
                r=estimate(count,topology,low,rp,rg,args.local_ohms,args.source_ohms,args.bus_volts,args.fuse_ohms,args.common_ohms,args.hub_watts)
                writer.writerow([count,topology,low,r['positive_current'],r['min_voltage'],r['input_watts']+args.hub_watts])
        return
    if args.faults:
        write_faults(args)
        return
    rp = args.contact_ohms + args.copper_ohms + 2*args.fuse_ohms
    rg = args.contact_ohms + args.copper_ohms
    print(f'ASSUMPTIONS: Rpositive={rp:g}, Rreturn={rg:g}, Rlocal={args.local_ohms:g} ohm. '
          f'Fuse resistance {args.fuse_ohms:g} ohm each. No measured resistance or efficiency data.', file=sys.stderr)
    print(f'Reference limits {args.branch_limit_amps:g}A/branch and {args.total_limit_amps:g}A total are REQUIRED DESIGN ASSUMPTIONS. '
          'The ideal continuous fault limiter is not the implemented latch-off input breaker. Cases outside limits are unconstrained estimates, not operating points.', file=sys.stderr)
    fields=['tiles','topology','watts_per_tile','branches','min_protected_V','max_positive_A','max_return_A',
            'max_hub_branch_A','max_local_A','total_hub_A','input_with_hub_W','loss_W','status']
    writer = csv.writer(sys.stdout)
    writer.writerow(fields)
    for count in (20, 64):
        for watts in (0.5, 3., 6., 14.):
            for position in ('chain','center','edge','corner'):
                r = estimate(count, position, watts, rp, rg, args.local_ohms, args.source_ohms, args.bus_volts, args.fuse_ohms, args.common_ohms, args.hub_watts)
                if r is None:
                    writer.writerow([count,position,watts]+['']*9+['NO_POSITIVE_ALL_LOADS_ON_DC_SOLUTION'])
                    continue
                status=['CONTACT_CURRENT_UNQUALIFIED']
                if r['min_voltage'] < 15.75: status.append('BELOW_WORST_CASE_SOURCE_STARTUP')
                if max(r['positive_current'],r['local_current']) > args.fuse_continuous_amps: status.append('EXCEEDS_FUSE_CONTINUOUS_BUDGET')
                if args.contact_screen_amps and max(r['positive_current'], r['return_current']) > args.contact_screen_amps:
                    status.append('EXCEEDS_ASSUMED_CONTACT_SCREEN')
                if r['source_current'] > args.branch_limit_amps: status.append('EXCEEDS_ASSUMED_HUB_BRANCH_LIMIT')
                if r['total_current'] > args.total_limit_amps: status.append('EXCEEDS_ASSUMED_HUB_TOTAL_LIMIT')
                if r['local_current'] > 0.95/1.01: status.append('EXCEEDS_SOURCE_ILIM_MIN')
                if r['input_watts']+args.hub_watts > 100: status.append('EXCEEDS_100W_INPUT')
                writer.writerow([count,position,watts,r['branches']]+[f'{r[k]:.6f}' for k in (
                    'min_voltage','positive_current','return_current','source_current','local_current','total_current')]
                    +[f'{r["input_watts"]+args.hub_watts:.6f}',f'{r["loss_watts"]:.6f}',
                      '+'.join(status) or 'DC_LIMITS_ONLY_NOT_QUALIFIED'])


if __name__ == '__main__':
    main()
