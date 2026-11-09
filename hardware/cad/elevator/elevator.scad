// Printed pin-chain lift prototype. Units: mm. No physical fit or endurance test yet.
include <../common/tile_dimensions.scad>
$fn = 48;
part = "assembly";
show_references = true;
print_orientation = false;
chain_pitch = 24;
sprocket_pins = 6;
straight_links = 12;
carrier_stride = 2;
pin_clearance = 0.25;
chain_y = -8;
lower_axis = 52;
axis_spacing = straight_links * chain_pitch;
upper_axis = lower_axis + axis_spacing;
pitch_radius = chain_pitch / (2 * sin(180 / sprocket_pins));
carrier_offset = 18;
spoon_half_width = 4.2;
rail_spacing = 6;
rail_width = 2.4;
rail_height = 5;
frame_height = 394;
frame_split = 200;
base_thickness = 4;
magnet_pocket_depth = 3.2;
pcb_top = 90;
pcb_thickness = 1.6;
pcb_y = 15;
motor_width = 10;
motor_height = 12;
motor_length = 25.6;
motor_face_y = 7;
motor_shaft_length = 9;
motor_shaft_diameter = 3;
motor_clearance = 0.2;
hinge_nut_height = 1.6; // Test hardware requirement, not a measured sample.
drive_disc_y = 6.8;
track_marble_height = 13.5;
exit_marble_height = track_marble_height + 17 * tile_height;
release_height = upper_axis + pitch_radius*cos(30) + carrier_offset;
exit_rail_top = release_height - sqrt(8*8-pow(rail_spacing-rail_width/2,2));
// Vishay 81147 rev 1.0, drawing 6.550-5040.01-4 issue 2.
index_y = chain_y - 6.75;
sensor_base_z = lower_axis + 14.8 + 10.8 - 2.6;

assert(sprocket_pins == 6);
assert(spoon_half_width + 0.5 < rail_spacing - rail_width/2);
assert(motor_face_y + motor_length + 3 < tile_size/2-2);
assert(pcb_top - pcb_thickness > lower_axis + motor_height/2 + 10);
assert(drive_disc_y - (4 + hinge_nut_height) >= 1);
assert(base_thickness - magnet_pocket_depth >= 0.8-0.001);

module y_cylinder(d, h) { rotate([-90,0,0]) cylinder(d=d,h=h); }
module bolt_y(x,z,d=3.2) { translate([x,24,z]) y_cylinder(d,18); }
module d_shaft_hole(h) {
    intersection() {
        y_cylinder(motor_shaft_diameter+0.15,h);
        translate([-2,-0.1,-2]) cube([3.1,h+0.2,4]);
    }
}

module link_body() {
    difference() {
        union() {
            // One tongue and a two-ear clevis. M2 x 16 pin, nut and exposed drive tip.
            for (y=[-4,2]) translate([0,y,0]) y_cylinder(6.4,2);
            translate([-3,-4,0]) cube([6,2,8]);
            translate([-3,2,0]) cube([6,2,8]);
            translate([-3,-4,6]) cube([6,8,2]);
            translate([-3,-1.5,7]) cube([6,3,17]);
            translate([0,-1.5,chain_pitch]) y_cylinder(6.4,3);
        }
        for (z=[0,chain_pitch]) translate([0,-5,z]) y_cylinder(2+pin_clearance,11);
    }
}

module carrier() {
    union() {
        link_body();
        difference() {
            union() {
                translate([0,-3,9.6]) cube([carrier_offset,6,4.8]);
                intersection() {
                    translate([carrier_offset,0,2]) cylinder(r=10,h=10);
                    translate([5,-spoon_half_width,1]) cube([24,2*spoon_half_width,12]);
                }
            }
            translate([carrier_offset,0,12]) sphere(r=8.4);
            translate([7,-12,12]) cube([22,24,5]);
        }
    }
}

module sprocket(idler=false) {
    difference() {
        union() {
            translate([0,drive_disc_y,0]) y_cylinder(51,4);
            // Move the drive index disc forward so the sensor's rear arm clears the wheel.
            if(!idler) translate([0,-7.5,0]) y_cylinder(30,1.5);
            translate([0,idler ? 2.5 : -7.5,0]) y_cylinder(14,idler ? 11.5 : 20.2);
        }
        for (a=[0:360/sprocket_pins:359]) rotate([0,a,0]) {
            translate([pitch_radius,5,0]) y_cylinder(2+2*pin_clearance+0.4,6);
            translate([pitch_radius,5,-1.45]) cube([6,6,2.9]);
        }
        if (idler) {
            translate([0,2,0]) y_cylinder(3.3,13);
            translate([0,2,0]) y_cylinder(8,8.1);
            // One 623ZZ, nominal 3 x 10 x 4. Adjust seat only after a print fit test.
            translate([0,10,0]) y_cylinder(10.0,4.1);
        } else {
            translate([0,5,0]) d_shaft_hole(10);
            translate([0,11,0]) rotate([0,90,0]) cylinder(d=2.5,h=9);
        }
        // Six optical edges per revolution for the external TCST2103 index sensor.
        // Open the index rim. A closed outer rim cannot interrupt a slot sensor.
        if(!idler) for (a=[0:60:359]) rotate([0,a+30,0])
            translate([9,-7.6,-1.5]) cube([7,1.7,3]);
    }
}

module axle_spacer(h) {
    difference() { y_cylinder(4.8,h); translate([0,-0.1,0]) y_cylinder(3.2,h+0.2); }
}
module motor_saddle() {
    difference() {
        union() {
            translate([-14,5,lower_axis-10]) cube([28,15,6]);
            translate([-8,5,lower_axis-8]) cube([16,2,16]);
            for (x=[-11,11]) translate([x,14,lower_axis-10]) cylinder(d=7,h=16.2);
            for (x=[-12,8]) translate([x,18,lower_axis-10]) cube([4,19,6]);
        }
        translate([-motor_width/2-motor_clearance,motor_face_y,lower_axis-motor_height/2-motor_clearance])
            cube([motor_width+2*motor_clearance,motor_length+1,motor_height+2*motor_clearance]);
        translate([0,4,lower_axis]) y_cylinder(3.6,5);
        for (x=[-11,11]) translate([x,14,lower_axis-11]) cylinder(d=3.2,h=21);
    }
}
module motor_strap() {
    difference() {
        union() {
            translate([-15,10,lower_axis+6.2]) cube([30,8,3]);
            translate([-5,11,lower_axis+5.8]) cube([10,6,0.5]);
        }
        for (x=[-11,11]) translate([x,14,lower_axis+6]) cylinder(d=3.2,h=4);
    }
}

pcb_holes = [[-27,34],[27,34],[-14,-4],[14,-4]];
module pcb_supports() {
    for (xy=pcb_holes) difference() {
        union() {
            translate([xy[0]-3,xy[1]-3,pcb_top-pcb_thickness-8]) cube([6,37-xy[1],3]);
            translate([xy[0],xy[1],pcb_top-pcb_thickness-5]) cylinder(d=6,h=5);
        }
        translate([xy[0],xy[1],pcb_top-pcb_thickness-8.1])
            cylinder(d=pcb_screw_clearance,h=8.3);
        translate([xy[0],xy[1],pcb_top-pcb_thickness-8.1])
            cylinder(d=pcb_nut_af/cos(30),h=pcb_nut_depth+.1,$fn=6);
    }
}
module back_frame(z0,z1) {
    difference() {
        union() {
            translate([-60,31,z0]) cube([120,3,z1-z0]);
            for (x=[-60,54]) translate([x,25,z0]) cube([6,9,z1-z0]);
            if(z0<362 && z1>346) translate([-73,31,346]) cube([19,3,16]);
        }
        // Motor leads and the removable rear electronics access.
        translate([-10,24,lower_axis-12]) cube([20,15,30]);
        translate([-32,24,pcb_top-7]) cube([64,15,22]);
        for (x=[-57,57]) for (z=[frame_split-6,frame_split+6]) bolt_y(x,z);
        hull() for (z=[upper_axis-3,upper_axis+3]) bolt_y(0,z);
        for(x=[-57.5,-67.5]) bolt_y(x,354);
        for(x=[-5,5]) bolt_y(x,sensor_base_z+2);
        // Two 2.5mm cable ties retain the motor/sensor looms outside the access window.
        for(x=[-18,-12]) translate([x-1.6,24,73.1]) cube([3.2,15,1.8]);
        for(x=[12,18]) translate([x-1.6,24,107.1]) cube([3.2,15,1.8]);
        for(x=[-57,57]) for(z=x>0 ? [lower_axis,180,220,upper_axis] : [lower_axis,upper_axis]) bolt_y(x,z);
        for(z=[30,190,210,370]) for(x=[-61,53])
            translate([x,28,z]) rotate([0,90,0]) cylinder(d=2.5,h=9);
    }
}
module lower_frame() {
    union() {
        difference() {
            translate([-tile_size,-tile_size/2,0]) cube([2*tile_size,tile_size,base_thickness]);
            for (cx=[-40,40]) for (x=[-mount_spacing,mount_spacing])
                for (y=[-mount_spacing,mount_spacing]) translate([cx+x,y,-0.1])
                    cylinder(d=6.25,h=magnet_pocket_depth+0.1);
            translate([-53,chain_y-5,1.8]) cube([106,10,base_thickness-1.8+0.1]);
            // Keep a wiring opening at the first cell's unresolved module interface.
            translate([-55,-8,-0.1]) cube([30,16,base_thickness+0.2]);
        }
        back_frame(0,frame_split);
        motor_saddle();
        pcb_supports();
        pawl_mount();
        feed_fork();
    }
}
module upper_frame() { back_frame(frame_split,frame_height); }
module splice() {
    difference() {
        translate([-5,34,frame_split-12]) cube([10,3,24]);
        for(z=[frame_split-6,frame_split+6]) bolt_y(0,z);
    }
}
module pawl() {
    difference() {
        translate([0,5,0]) rotate([90,0,0]) linear_extrude(3)
            polygon([[23,101],[34,101],[34,129],[34,137],[46,137],[46,127],
                     [35.6,127],[35.6,94],[30,94]]);
        translate([40,1,132]) y_cylinder(3.2,5);
        translate([36,1,132]) y_cylinder(2.3,5);
    }
}
module pawl_mount() {
    difference() {
        union() {
            translate([34,5,127]) cube([12,3,10]);
            for(x=[34,43]) translate([x,8,127]) cube([3,26,10]);
        }
        translate([40,4,132]) y_cylinder(3.2,6);
    }
    translate([36,2,132]) y_cylinder(2,3);
}

module rail(a,b) {
    intersection() {
        hull() for (q=[a,b]) translate([q[0],q[1]-rail_width/2,q[2]-rail_height])
            cube([0.1,rail_width,rail_height]);
        // End exactly at the interface plane; avoid the hull's 0.1mm overhang.
        translate([min(a[0],b[0]),-50,-50]) cube([abs(b[0]-a[0]),100,500]);
    }
}
module feed_fork() {
    union() {
        for (s=[-1,1]) {
            rail([-6,chain_y+s*rail_spacing,6.4],[55,chain_y+s*rail_spacing,7.1]);
            rail([55,chain_y+s*rail_spacing,7.1],[80,s*rail_spacing,7.1]);
            translate([-6,chain_y+s*rail_spacing-rail_width/2,1.4]) cube([3,rail_width,12]);
        }
        translate([58,-17,0]) cube([5,30,3]);
    }
}
module exit_fork() {
    union() {
        for (s=[-1,1]) {
            rail([4,chain_y+s*rail_spacing,exit_rail_top],[-55,chain_y+s*rail_spacing,360]);
            rail([-55,chain_y+s*rail_spacing,360],[-80,s*rail_spacing,exit_marble_height-6.4]);
        }
        translate([-63,-17,354]) cube([5,30,2]);
        translate([-72,8,354]) cube([14,5,4]);
        // Mount outside the full rotating carrier sweep.
        for (x=[-60,-70]) difference() {
            translate([x,8,350]) cube([5,23,8]);
            translate([x+2.5,20,354]) y_cylinder(2.5,12);
        }
    }
}
module marble_guides() {
    for (y=[chain_y-10.8,chain_y+9.3]) {
        // 18.6mm channel, with spoon clearance on each side.
        translate([31,y,lower_axis]) cube([22,1.5,axis_spacing]);
        translate([31,y,12]) cube([22,1.5,lower_axis-12]);
        for (zaxis=[lower_axis,upper_axis])
            translate([0,y,zaxis]) rotate([-90,0,0]) linear_extrude(1.5)
                intersection() {
                    difference() { circle(r=zaxis==upper_axis ? 50 : 49); circle(r=27); }
                    translate([-51,zaxis==upper_axis ? -51 : 0]) square([102,51]);
                }
    }
    for(x=[54,-60]) for(z=x>0 ? [lower_axis,180,220,upper_axis] : [lower_axis,upper_axis]) {
        for(y=[chain_y-10.8,chain_y+9.3])
            translate([x>0 ? 46 : -60,y,z-3]) cube([14,1.5,6]);
        difference() {
            translate([x,chain_y-10.8,z-3]) cube([6,34-chain_y+10.8,6]);
            translate([x+3,22,z]) y_cylinder(2.5,13);
        }
    }
}
module guard(z0,z1) {
    difference() {
        union() {
            translate([-62,-23,z0]) cube([124,1.5,z1-z0]);
            for (x=[-62,60.5]) translate([x,-23,z0]) cube([1.5,57,z1-z0]);
        }
        translate([30,-25,3]) cube([36,52,22]);
        translate([-66,-25,344]) cube([38,52,40]);
        // Clearance for the fixed sensor flange, its screws and the removable bracket.
        translate([-8.5,-28,sensor_base_z-7]) cube([17,8,14]);
        for(z=[30,190,210,370]) for(x=[-63,59])
            translate([x,28,z]) rotate([0,90,0]) cylinder(d=3.2,h=5);
    }
}

right_nodes = [for (i=[0:straight_links]) [pitch_radius,lower_axis+i*chain_pitch]];
top_nodes = [for (a=[60:60:180]) [pitch_radius*cos(a),upper_axis+pitch_radius*sin(a)]];
left_nodes = [for (i=[1:straight_links]) [-pitch_radius,upper_axis-i*chain_pitch]];
bottom_nodes = [for (a=[240:60:300]) [pitch_radius*cos(a),lower_axis+pitch_radius*sin(a)]];
nodes = concat(right_nodes,top_nodes,left_nodes,bottom_nodes);
module link_at(a,b,with_cup=true) {
    translate([a[0],chain_y,a[1]]) rotate([0,atan2(b[0]-a[0],b[1]-a[1]),0])
        if(with_cup) carrier(); else link_body();
}
module chain() {
    for (i=[0:len(nodes)-1]) link_at(nodes[i],nodes[(i+1)%len(nodes)],i%carrier_stride==0);
}
module motor_reference() {
    // Manufacturer envelope only, not a supplier STEP or tested fit.
    translate([-motor_width/2,motor_face_y,lower_axis-motor_height/2])
        cube([motor_width,motor_length,motor_height]);
    translate([0,motor_face_y-motor_shaft_length,lower_axis])
        y_cylinder(motor_shaft_diameter,motor_shaft_length);
}
module pcb_reference() {
    translate([0,pcb_y,pcb_top-pcb_thickness]) linear_extrude(pcb_thickness)
        difference() {
            polygon([[-30,22],[30,22],[30,-8],[16,-8],[16,-22],[-16,-22],
                     [-16,-8],[-30,-8]]);
            for (xy=pcb_holes) translate([xy[0],xy[1]-pcb_y]) circle(d=2.5);
        }
}

module index_sensor_bracket() {
    difference() {
        union() {
            translate([-8,index_y-12.4,sensor_base_z]) cube([16,31-index_y+12.4,3]);
            translate([-8,28,sensor_base_z-4]) cube([16,3,10]);
            for(x=[-8,6]) translate([x,1,sensor_base_z-4]) cube([2,29,4.1]);
        }
        for(y=[index_y-9.5,index_y+9.5])
            translate([0,y,sensor_base_z-0.1]) cylinder(d=3.3,h=3.2);
        // Four leads exit outward from the flange; leave solder and wire access.
        translate([-3,index_y-5.6,sensor_base_z-0.1]) cube([6,11.2,3.2]);
        for(x=[-5,5]) translate([x,27,sensor_base_z+2]) y_cylinder(3.2,5);
    }
}
module index_sensor_reference() {
    // Conservative nominal package envelope, not a supplier STEP or a fit qualification.
    difference() {
        union() {
            translate([-3.15,index_y-12.25,sensor_base_z-3.1]) cube([6.3,24.5,3.1]);
            for(y=[index_y-5.95,index_y+1.55])
                translate([-3.15,y,sensor_base_z-10.8]) cube([6.3,4.4,7.7]);
        }
        for(y=[index_y-9.5,index_y+9.5])
            translate([0,y,sensor_base_z-3.2]) cylinder(d=3.3,h=3.3);
    }
}
module elevator_assembly() {
    lower_frame(); upper_frame(); motor_strap(); pawl(); index_sensor_bracket();
    for(x=[-57,57]) translate([x,0,0]) splice();
    translate([0,chain_y,lower_axis]) sprocket();
    translate([0,chain_y,upper_axis]) sprocket(true);
    // Recessed M3x40 head, front spacer, 623-2Z and rear spacer clamp the inner race.
    // Nominal axial stack only; verify the purchased bearing and printed fit.
    translate([0,-0.5,upper_axis]) axle_spacer(2.5);
    translate([0,6,upper_axis]) axle_spacer(25);
    chain(); exit_fork(); marble_guides();
}

module selected_part() {
if(part=="link") link_body();
else if(part=="carrier") carrier();
else if(part=="drive") sprocket();
else if(part=="idler") sprocket(true);
else if(part=="spacer_front") axle_spacer(2.5);
else if(part=="spacer_rear") axle_spacer(25);
else if(part=="splice") splice();
else if(part=="pawl") pawl();
else if(part=="strap") motor_strap();
else if(part=="sensor_bracket") index_sensor_bracket();
else if(part=="sensor_collision") intersection() {
    // Exclude the intended zero-thickness flange/bracket support contact.
    translate([0,0,-0.01]) index_sensor_reference();
    union() {
        // Continuous rotational envelope contains the wheel at every angle.
        translate([0,chain_y,lower_axis]) {
            translate([0,drive_disc_y,0]) y_cylinder(51,4);
            translate([0,-7.5,0]) y_cylinder(30,1.5);
            translate([0,-7.5,0]) y_cylinder(14,20.2);
        }
        chain(); motor_reference(); pcb_reference(); index_sensor_bracket();
    }
}
else if(part=="sensor_guard_collision") intersection() {
    union() { index_sensor_reference(); index_sensor_bracket(); }
    guard(0,frame_split);
}
else if(part=="lower_frame") lower_frame();
else if(part=="upper_frame") upper_frame();
else if(part=="feed") feed_fork();
else if(part=="exit") exit_fork();
else if(part=="guard_lower") guard(0,frame_split);
else if(part=="guard_upper") guard(frame_split,frame_height);
else if(part=="guides_lower") intersection() { marble_guides(); translate([-65,-25,0]) cube([130,65,frame_split]); }
else if(part=="guides_upper") intersection() { marble_guides(); translate([-65,-25,frame_split]) cube([130,65,frame_height-frame_split]); }
else if(part=="pcb_collision") intersection() { chain(); pcb_reference(); }
else if(part=="base_chain_collision")
    union() {
        // Lower half-turn only. The upper half of this wheel is not a chain path.
        for(a=concat([0:5:30],[210:5:355])) intersection() {
            translate([0,chain_y,lower_axis]) rotate([0,-a,0])
                translate([pitch_radius*cos(30),0,-chain_pitch/2]) carrier();
            lower_frame();
        }
        // Conservative swept envelopes for both straight legs, including every carrier height.
        for(side=[-1,1]) intersection() {
            hull() for(z=[lower_axis,upper_axis])
                translate([side*pitch_radius,chain_y,z])
                    rotate([0,side>0 ? 0 : 180,0]) carrier();
            lower_frame();
        }
    }
else if(part=="feed_collision" || part=="exit_collision")
    for(a=[0:5:355]) intersection() {
        translate([0,chain_y,part=="feed_collision" ? lower_axis : upper_axis])
            rotate([0,-a,0]) translate([pitch_radius*cos(30),0,-chain_pitch/2]) carrier();
        if(part=="feed_collision") feed_fork(); else exit_fork();
    }
else {
    elevator_assembly();
    if ($preview) {
        color([0.5,0.5,0.5,0.2]) guard(0,frame_height);
        if(show_references) {
            color("gray") motor_reference();
            color("green") pcb_reference();
            color("black") index_sensor_reference();
        }
    }
}
}
if(print_orientation) {
    if(part=="link") translate([0,0,4]) rotate([90,0,0]) selected_part();
    else if(part=="carrier") translate([0,0,4.2]) rotate([90,0,0]) selected_part();
    else if(part=="drive") translate([0,0,7.5]) rotate([90,0,0]) selected_part();
    else if(part=="idler") translate([0,0,-2.5]) rotate([90,0,0]) selected_part();
    else if(part=="spacer_front" || part=="spacer_rear") rotate([90,0,0]) selected_part();
    else if(part=="splice") translate([0,0,-34]) rotate([90,0,0]) selected_part();
    else if(part=="pawl") translate([0,0,-2]) rotate([90,0,0]) selected_part();
    else if(part=="strap") translate([0,0,lower_axis+9.2]) rotate([180,0,0]) selected_part();
    else if(part=="sensor_bracket") translate([-(sensor_base_z-4),0,8]) rotate([0,90,0]) selected_part();
    else if(part=="upper_frame") translate([0,-frame_split,34]) rotate([-90,0,0]) selected_part();
    else selected_part();
} else selected_part();
