"""Local engineering regression checks; no component or physical qualification implied."""
import csv
import os
import importlib.util
import io
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


power=load('power_budget');checker=load('check_tile_netlist');hub=load('check_hub_netlist');limits=load('hub_limits');runner=load('run_checks');logic=load('shutdown_logic');distribution=load('distribution')


class EngineeringChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get('KLINK_NETLIST_DIR'):
            cls.output=Path(os.environ['KLINK_NETLIST_DIR'])
        else:
            cls.directory=tempfile.TemporaryDirectory(prefix='.klink-netlists-',dir=Path.home())
            cls.addClassCleanup(cls.directory.cleanup)
            cls.output=Path(cls.directory.name)
            runner.export_netlists(cls.output)

    def test_single_load_analytic_voltage(self):
        r=power.estimate(1,'chain',3,.22,.07,.225,.15,20)
        resistance=.22-.075+.15+.07+.225
        expected=(20+math.sqrt(400-4*resistance*3))/2
        self.assertAlmostEqual(r['min_voltage'],expected,places=6)
        self.assertLess(r['energy_residual'],1e-5)

    def test_zero_load_all_geometries(self):
        for count in (20,64):
            for location in ('chain','center','edge','corner'):
                with self.subTest(count=count,location=location):
                    self.assertEqual(len(power.geometry(count,location)[0]),count)
                    r=power.estimate(count,location,0,.22,.07,.225,.15,20)
                    self.assertAlmostEqual(r['min_voltage'],20,places=6)
                    self.assertAlmostEqual(r['input_watts'],0,places=6)

    def test_two_cell_hub_port_counts(self):
        for place,ports in [('center',6),('edge',4),('corner',3)]:
            tiles,hub=power.geometry(20,place)
            self.assertEqual(len(power.links(tiles,hub)[1]),ports)

    def test_short_current_is_limited_by_assumed_source(self):
        r=power.fault_snapshot(1,'chain',0)
        self.assertAlmostEqual(r['short_current'],1.5,places=6)
        self.assertAlmostEqual(r['total'],1.5,places=6)
        self.assertAlmostEqual(r['max_return'],1.5,places=6)

    def test_grid_ground_current_is_not_bounded_by_one_branch_limit(self):
        tiles,hub=power.geometry(20,'edge');node=power.links(tiles,hub)[1][0]
        first=power.fault_snapshot(20,'edge',node)
        second=power.fault_snapshot(20,'edge',node,opened=first['next_open'])
        self.assertLessEqual(second['total'],4.500001)
        self.assertAlmostEqual(second['short_current'],second['total'],places=6)
        self.assertGreater(second['max_return'],2)
        self.assertGreater(second['max_positive'],first['max_positive'])

    def test_variable_fuse_resistance_matches_analytic_case(self):
        r=power.estimate(1,'chain',3,.47,.07,.225,.15,20,fuse_r=.2)
        resistance=.47-.2+.15+.07+.225
        expected=(20+math.sqrt(400-4*resistance*3))/2
        self.assertAlmostEqual(r['min_voltage'],expected,places=6)

    def test_requested_fault_limits_are_applied(self):
        r=power.fault_snapshot(1,'chain',0,branch_limit=.8,total_limit=.6)
        self.assertAlmostEqual(r['total'],.6,places=5)

    def test_open_return_redistributes_fault_current(self):
        tiles,hub=power.geometry(20,'corner');node=power.links(tiles,hub)[1][0]
        closed=power.fault_snapshot(20,'corner',node)
        opened=power.fault_snapshot(20,'corner',node,opened_return=('branch',0))
        self.assertAlmostEqual(opened['short_current'],opened['total'],places=6)
        self.assertLessEqual(opened['total'],4.500001)
        self.assertNotAlmostEqual(closed['max_return'],opened['max_return'],places=3)

    def test_ground_mesh_open_can_exceed_original_maximum(self):
        tiles,hub=power.geometry(20,'edge');node=power.links(tiles,hub)[1][0]
        r=power.fault_snapshot(20,'edge',node,opened_return=('edge',1,5))
        self.assertGreater(r['max_return'],3.5)
        self.assertLessEqual(r['max_return'],r['total'])
        self.assertAlmostEqual(r['total'],4.5,places=5)

    def test_load_csv_is_rectangular_and_contains_32_cases(self):
        result=subprocess.run([sys.executable,str(HERE/'power_budget.py')],capture_output=True,text=True,check=True)
        rows=list(csv.reader(io.StringIO(result.stdout)))
        self.assertEqual(len(rows),33)
        self.assertTrue(all(len(row)==len(rows[0]) for row in rows))
        self.assertIn('REQUIRED DESIGN ASSUMPTIONS',result.stderr)

    def test_nonfinite_resistance_is_rejected(self):
        r=subprocess.run([sys.executable,str(HERE/'power_budget.py'),'--contact-ohms','nan'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)

    def test_current_netlist(self):
        checks,components,nets,missing=checker.inspect(self.output/'tile.xml')
        self.assertGreater(checks,300)
        self.assertEqual(missing,['J3','J4','J5','J6','J7'])

    def test_rtn_ground_strap_is_rejected(self):
        tree=ET.parse(self.output/'tile.xml');root=tree.getroot()
        node=next(n for net in root.findall('./nets/net') for n in net if n.attrib.get('ref')=='U5' and n.attrib.get('pin')=='17')
        for net in root.findall('./nets/net'):
            if node in list(net):net.remove(node)
        next(net for net in root.findall('./nets/net') if net.attrib['name']=='GND').append(node)
        with tempfile.NamedTemporaryFile(suffix='.xml') as file:
            tree.write(file.name)
            with self.assertRaises(ValueError):checker.inspect(file.name)

    def test_hub_connections_and_calculation_values(self):
        checks,parts,nets=hub.inspect(self.output/'hub.xml')
        self.assertGreater(checks,200)
        self.assertEqual(parts,214)

    def test_hub_bad_shunt_sense_is_rejected(self):
        tree=ET.parse(self.output/'hub.xml')
        node=next(n for n in tree.getroot().findall('./nets/net/node')if n.attrib.get('ref')=='U4'and n.attrib.get('pin')=='7')
        node.attrib['pin']='8'
        with tempfile.NamedTemporaryFile(suffix='.xml')as file:
            tree.write(file.name)
            with self.assertRaises(ValueError):hub.inspect(file.name)

    def test_single_load_common_source_loss(self):
        r=power.estimate(1,'chain',3,.22,.07,.225,.15,20,common_r=.1)
        resistance=.22-.075+.15+.07+.225+.1
        expected=(20+math.sqrt(400-4*resistance*3))/2
        self.assertAlmostEqual(r['min_voltage'],expected,places=6)
        self.assertLess(r['energy_residual'],1e-5)

    def test_chain_voltage_collapse_and_nearby_analytic_roots(self):
        self.assertIsNone(power.estimate(20,'chain',3,.22,.07,.225,.15,20))
        self.assertIsNotNone(power.estimate(20,'chain',.5,.22,.07,.225,.15,20))
        # One-node maximum P = V^2/(4R). Test both sides independently.
        resistance=.22-.075+.15+.07+.225
        maximum=400/(4*resistance)
        self.assertIsNotNone(power.estimate(1,'chain',maximum*.999,.22,.07,.225,.15,20))
        self.assertIsNone(power.estimate(1,'chain',maximum*1.001,.22,.07,.225,.15,20))

    def test_hub_load_also_flows_through_common_resistance(self):
        r=power.estimate(1,'chain',0,.22,.07,.225,.15,20,common_r=.1,hub_watts=5)
        expected=(20+math.sqrt(400-4*.1*5))/2
        self.assertAlmostEqual(r['hub_voltage'],expected,places=6)
        self.assertAlmostEqual(r['total_current'],5/expected,places=6)
        self.assertAlmostEqual(r['input_watts']+5,20*5/expected,places=6)

    def test_one_bad_return_is_different_from_uniform_scaling(self):
        base=power.fault_snapshot(20,'edge',0)
        bad=power.fault_snapshot(20,'edge',0,return_overrides={('branch',0):.7})
        self.assertNotAlmostEqual(base['max_return'],bad['max_return'],places=3)
        self.assertAlmostEqual(bad['short_current'],bad['total'],places=5)

    def test_all_feeding_branches_must_open(self):
        tiles,hub_cells=power.geometry(20,'center');branches=power.links(tiles,hub_cells)[1]
        opened={('branch',k)for k in range(len(branches))}
        cut=power.fault_snapshot(20,'center',0,opened=opened)
        self.assertAlmostEqual(cut['short_current'],0,places=5)
        still_fed=power.fault_snapshot(20,'center',0,opened=opened-{('branch',0)})
        self.assertGreater(still_fed['short_current'],1)

    def test_hub_static_bounds_and_thermal_budget(self):
        for temperature in (-40,25,70,125):
            r=limits.limits(temperature)
            self.assertLess(r['trip_max_A'],4.5)
            self.assertLess(r['trip_with_1mV_overdrive_A'],r['backup_current_min_A'])
            self.assertGreater(r['trip_min_A'],4)
            self.assertLess(r['input_max_including_10mA_bypass_W'],100)
            self.assertGreater(r['ov_rising_V'][0],21)
            self.assertLess(r['uv_rising_V'][1],19)
            self.assertLess(r['shunt_loss_at_trip_W'],r['shunt_rated_W'])

    def test_footprint_files_and_pin_numbers(self):
        import re
        footprint_root=Path(os.environ.get('KICAD_FOOTPRINT_DIR','/usr/share/kicad/footprints'))
        for board in ('tile','hub'):
            root=ET.parse(self.output/f'{board}.xml').getroot()
            parts={c.attrib['ref']:c for c in root.findall('./components/comp')}
            for ref,c in parts.items():
                fp=c.findtext('footprint')
                if any(q.attrib.get('name')=='exclude_from_board'for q in c.findall('property')):continue
                if not fp:
                    self.assertEqual(board,'tile');self.assertIn(ref,['J3','J4','J5','J6','J7']);continue
                library,name=fp.split(':')
                directory=ROOT/'hardware/electronics/libraries/Klink.pretty'if library=='Klink'else footprint_root/(library+'.pretty')
                path=directory/(name+'.kicad_mod')
                self.assertTrue(path.is_file(),str(path))
                pads=set(re.findall(r'\(pad\s+"([^"\n]*)"',path.read_text()))
                connected={n.attrib['pin']for n in root.findall('./nets/net/node')if n.attrib['ref']==ref}
                self.assertFalse(connected-pads,(board,ref,connected-pads))

    def test_chain_drop_and_loss_lower_bounds(self):
        r=distribution.chain_diagnosis()
        self.assertEqual(r['first_branch_minimum_A'],3)
        self.assertAlmostEqual(r['optimistic_far_end_drop_V'],9.71875)
        self.assertAlmostEqual(sum(r['loss_lower_bound_W'].values()),20.55925)
        self.assertLess(r['failed_voltage_upper_bound_V'],0)
        self.assertLess(r['uniform_positive_DC_boundary_W_per_tile'][1],1.804)

    def test_removing_fuses_alone_does_not_fix_chain(self):
        r=distribution.operating_point('no_edge_fuses_old_contacts',20,'chain',3,bus=20)
        self.assertIsNotNone(r)
        self.assertLess(r['min_voltage'],15.75)
        self.assertFalse(distribution.eligible(r,'no_edge_fuses_old_contacts'))

    def test_normal_fuse_open_redistributes_load(self):
        before=distribution.operating_point('rev_a_fused',20,'center',3,bus=20)
        after=distribution.operating_point('rev_a_fused',20,'center',3,bus=20,opened=('branch',5))
        self.assertLess(before['positive_current'],.75)
        self.assertGreater(after['positive_current'],.75)
        self.assertAlmostEqual(after['positive_current'],.78980596,places=6)
        self.assertLess(after['energy_residual'],1e-5)

    def test_normal_missing_ground_rebalances_separately(self):
        before=distribution.operating_point('80m_loop_target',20,'corner',3)
        after=distribution.operating_point('80m_loop_target',20,'corner',3,opened_return=('branch',0))
        self.assertNotAlmostEqual(before['return_current'],after['return_current'],places=3)
        self.assertLess(after['energy_residual'],1e-5)

    def test_16_and_20_tile_mesh_targets(self):
        for count in (16,20):
            for topology in ('center','edge','corner'):
                r=distribution.operating_point('80m_loop_target',count,topology,3,bus=18.5)
                self.assertTrue(distribution.eligible(r,'80m_loop_target'),(count,topology,r))
        r=distribution.operating_point('40m_loop_target',20,'chain',3,bus=19)
        self.assertTrue(distribution.eligible(r,'40m_loop_target'))

    def test_disconnected_chain_is_not_reported_as_numeric_collapse(self):
        r=power.estimate(20,'chain',.5,.22,.07,.225,.15,20,opened=('edge',3,4),details=True)
        self.assertEqual(r['status'],'DISCONNECTED_ALL_LOADS_ON')

    def test_nonuniform_module_load_and_power_balance(self):
        loads=[.5]*20;loads[0]=8
        r=distribution.operating_point('80m_loop_target',20,'corner',loads)
        self.assertLess(r['energy_residual'],1e-5)
        self.assertAlmostEqual(r['input_watts']-r['loss_watts'],17.5,places=5)
        with self.assertRaises(ValueError):power.estimate(20,'chain',[3]*19,.22,.07,.225,.15,20)

    def test_finite_energy_does_not_bound_current_to_hub_trip(self):
        r=distribution.energy(12,21,.04)
        self.assertAlmostEqual(r['initial_A'],525)
        self.assertAlmostEqual(r['energy_J'],.002646)
        self.assertGreater(r['integral_A2s'],.0423)  # Comparison to nominal fuse I2t is not clearing proof.

    def test_each_output_overcurrent_shuts_every_output_during_startup(self):
        for k in range(6):
            model=logic.Shutdown(self.output/'hub.xml');model.step(control=False)
            oc=[True]*6;oc[k]=False
            r=model.step(ready=False,oc=oc,health=[False]*6)
            self.assertTrue(r['fault']);self.assertFalse(r['enabled']);self.assertEqual(r['port_enables'],[False]*6)

    def test_each_health_fault_latches_after_arming(self):
        for k in range(7):
            model=logic.Shutdown(self.output/'hub.xml');model.step(control=False);model.step(ready=True)
            health=[True]*6
            if k<6:health[k]=False
            r=model.step(ready=False,health=health,input_health=k<6)
            self.assertTrue(r['fault']);self.assertTrue(r['armed']);self.assertEqual(r['port_enables'],[False]*6)
            self.assertFalse(model.step(ready=True)['enabled'])
            self.assertFalse(model.step(control=False)['enabled'])
            self.assertTrue(model.step(ready=False)['enabled'])

    def test_failed_startup_trips_when_allowance_expires(self):
        model=logic.Shutdown(self.output/'hub.xml');model.step(control=False)
        self.assertTrue(model.step(ready=False,health=[False]*6)['enabled'])
        self.assertFalse(model.step(ready=True,health=[False]*6)['enabled'])

    def test_input_oc_and_pd_loss_disable_all_outputs(self):
        for args in (dict(input_oc=False),dict(pd=False)):
            model=logic.Shutdown(self.output/'hub.xml');model.step(control=False)
            self.assertEqual(model.step(**args)['port_enables'],[False]*6)

    def test_branch_trip_and_control_rail_margins(self):
        for temperature in (-40,25,70,125):
            r=limits.limits(temperature,limit_ohms=10000)
            self.assertGreater(r['trip_min_A'],3.8);self.assertLess(r['trip_max_A'],4.2)
            self.assertLess(r['trip_with_1mV_overdrive_A'],r['backup_current_min_A'])
            self.assertLess(r['control_release_max_V'],r['control_min_V'])
            self.assertGreater(r['control_assert_min_V'],2.7)
            self.assertLess(r['uv_rising_V'][1],18.5)
            self.assertGreater(r['uv_rising_V'][0],15.75)

    def test_port_ramp_capacitance_stays_above_device_minimum(self):
        minimum=22e-9*.95*(1-30e-6*100)
        self.assertGreater(minimum,10e-9)
        maximum=22e-9*1.05*(1+30e-6*100)
        ramp=21*maximum/(23.5*1.775e-6)
        self.assertLess(ramp+.0016,.180)  # Ramp plus power-good deglitch fits the startup allowance.

    def test_tvs_polarity_is_checked(self):
        tree=ET.parse(self.output/'hub.xml');root=tree.getroot()
        nodes=[n for n in root.findall('./nets/net/node')if n.attrib['ref']=='D100']
        for node in nodes:node.attrib['pin']='2'if node.attrib['pin']=='1'else'1'
        with tempfile.NamedTemporaryFile(suffix='.xml')as file:
            tree.write(file.name)
            with self.assertRaises(ValueError):hub.inspect(file.name)


if __name__=='__main__':unittest.main()
