// Gravity return for the pin-chain elevator. Coordinates are relative to its base.
// PETG fit prototype. Anchor M6 support rods to a rigid baseboard before use.
include <../common/tile_dimensions.scad>
$fn = 40;
part = "assembly"; // segment, saddle, entry_saddle, end_saddle, foot, kit_collision
segment_index = 0;
show_supports = true;
support_plane_z = -tile_height;
rod_top_allowance = 10; // Above the flat seat for washer, nut and exposed thread; verify actual hardware.
marble_diameter = 16;
channel_width = 18.5;
wall = 3;
radius = 120;
coil_center = [-240,-120];
entry_height = 13.5 + 17*tile_height;
return_height = 13.5;
lead_length = 160;
coil_length = 5*PI*radius;
straight_length = 320;
end_length = PI*radius;
total_length = lead_length+coil_length+straight_length+end_length;
piece_count = 27;
pitch_angle = atan((entry_height-return_height)/total_length);
function station(i) = i<=1 ? i*lead_length : i<=21 ? lead_length+(i-1)*coil_length/20 :
    i<=23 ? lead_length+coil_length+(i-21)*straight_length/2 :
    lead_length+coil_length+straight_length+(i-23)*end_length/4;
function height(s) = entry_height-(entry_height-return_height)*s/total_length;
function point(s) = s<=lead_length ? [-80-s,0,height(s)] :
    s<=lead_length+coil_length ?
        let(a=90+(s-lead_length)*180/(PI*radius))
        [coil_center[0]+radius*cos(a),coil_center[1]+radius*sin(a),height(s)] :
    s<=lead_length+coil_length+straight_length ?
        [coil_center[0]+s-lead_length-coil_length,-240,height(s)] :
        let(a=270+(s-lead_length-coil_length-straight_length)*180/(PI*radius))
        [80+radius*cos(a),-120+radius*sin(a),height(s)];
function heading(s) = s<lead_length ? 180 : s<lead_length+coil_length ?
    180+(s-lead_length)*180/(PI*radius) :
    s<lead_length+coil_length+straight_length ? 0 :
    360+(s-lead_length-coil_length-straight_length)*180/(PI*radius);
function is_curve(i) = (i>=1 && i<=20) || i>=23;
function piece_length(i) = station(i+1)-station(i);
function local_angle(t,curved) = curved ? t*180/(PI*radius) : 0;
function local_point(t,curved) = curved ?
    [radius*sin(local_angle(t,true)),radius*(1-cos(local_angle(t,true))),-t*tan(pitch_angle)] :
    [t,0,-t*tan(pitch_angle)];
assert(segment_index>=0 && segment_index<piece_count);
assert(channel_width>marble_diameter+2);
assert(abs(point(total_length)[0]-80)<0.001 && abs(point(total_length)[1])<0.001);
assert(coil_center[0]==-80-lead_length);
assert(return_height-11.1>0);
echo(return_length_mm=total_length, slope_degrees=pitch_angle);
module at_station(s) {
    translate(point(s)) rotate([0,0,heading(s)]) rotate([0,pitch_angle,0]) children();
}
module local_frame(t,curved,tilt=true) {
    translate(local_point(t,curved)) rotate([0,0,local_angle(t,curved)])
        rotate([0,tilt ? pitch_angle : 0,0]) children();
}
module slice(t,curved,w,z0,z1) {
    local_frame(t,curved) translate([-0.06,-w/2,z0]) cube([0.12,w,z1-z0]);
}
module sweep(t0,t1,curved,w,z0,z1) {
    steps=ceil((t1-t0)/4);
    for(k=[0:steps-1]) hull() {
        slice(t0+(t1-t0)*k/steps,curved,w,z0,z1);
        slice(t0+(t1-t0)*(k+1)/steps,curved,w,z0,z1);
    }
}
module ears(t,curved,inward) {
    local_frame(t,curved) for(y=[-17,17]) difference() {
        hull() {
            translate([inward*5,y,-11]) cylinder(d=7,h=3.2);
            translate([inward*5,sign(y)*13,-11]) cylinder(d=7,h=3.2);
        }
        translate([inward*5,y,-11.1]) cylinder(d=3.2,h=3.4);
    }
}
module segment_shape(curved,length) {
    union() {
        intersection() {
            difference() {
                sweep(-2,length+2,curved,channel_width+2*wall,-11,10);
                sweep(-2.1,length+2.1,curved,channel_width,-8,8.5);
                // Retaining lips leave a 14.5mm opening and 0.5mm above the nominal ball.
                sweep(-2.1,length+2.1,curved,channel_width-4,8.49,11);
            }
            // Vertical butt faces match both elevator forks and adjacent printed segments.
            local_frame(0,curved,false) translate([0,-500,-500]) cube([1000,1000,1000]);
            local_frame(length,curved,false) translate([-1000,-500,-500]) cube([1000,1000,1000]);
        }
        ears(0,curved,1); ears(length,curved,-1);
    }
}
module segment(i) {
    translate(point(station(i))) rotate([0,0,heading(station(i))])
        segment_shape(is_curve(i),piece_length(i));
}
module saddle(offset=0) {
    x0=offset==0 ? -12 : offset>0 ? 1 : offset-12;
    span=offset==0 ? 24 : abs(offset)+11;
    difference() {
        union() {
            translate([x0,-32,-14]) cube([span,64,3]);
            // Flat washer seats on vertical rods; central plate follows the track slope.
            for(y=[-27,27]) translate([offset,y,-14]) rotate([0,-pitch_angle,0])
                translate([0,0,-1.8]) cylinder(d=14,h=5.8);
        }
        for(x=offset==0 ? [-5,5] : [sign(offset)*5]) for(y=[-17,17])
            translate([x,y,-14.1]) cylinder(d=3.2,h=3.2);
        for(y=[-27,27]) translate([offset,y,-14]) rotate([0,-pitch_angle,0])
            translate([0,0,-2]) cylinder(d=6.5,h=8);
        if(offset>0) translate([0,-9,-14.1]) cube([4,18,3.2]);
    }
}
module foot() {
    difference() {
        translate([-18,-34,0]) cube([36,68,6]);
        for(y=[-27,27]) translate([0,y,-0.1]) cylinder(d=6.5,h=6.2);
        for(x=[-12,12]) for(y=[-17,17]) translate([x,y,-0.1]) cylinder(d=4.5,h=6.2);
    }
}
function support_offset(i) = i==0 ? 34 : i==piece_count ? -34 : 0;
// Repeated helix joints share one continuous column, sized from its highest joint.
support_stations = [0,2,4,6,8,22,24,26,27];
module support(i) {
    s=station(i); offset=support_offset(i);
    dx=offset*cos(pitch_angle)-14*sin(pitch_angle);
    xy=[point(s)[0]+dx*cos(heading(s)),point(s)[1]+dx*sin(heading(s))];
    translate([xy[0],xy[1],support_plane_z]) rotate([0,0,heading(s)]) {
        foot();
        if($preview || part=="kit_collision") color("silver") for(y=[-27,27])
            translate([0,y,-support_board_thickness-support_rod_underboard])
                cylinder(d=6,h=point(s)[2]-support_plane_z+support_board_thickness+support_rod_underboard+6-
                offset*sin(pitch_angle)-14*cos(pitch_angle)+rod_top_allowance-2);
    }
}
module support_board() {
    difference() {
        translate([support_board_origin[0],support_board_origin[1],support_plane_z-support_board_thickness])
            cube([support_board_size[0],support_board_size[1],support_board_thickness]);
        for(i=support_stations) {
            s=station(i);offset=support_offset(i);
            dx=offset*cos(pitch_angle)-14*sin(pitch_angle);
            translate([point(s)[0]+dx*cos(heading(s)),point(s)[1]+dx*sin(heading(s)),
                       support_plane_z-support_board_thickness-.1]) rotate([0,0,heading(s)]) {
                for(y=[-27,27]) translate([0,y,0]) cylinder(d=6.5,h=support_board_thickness+.2);
                for(x=[-12,12]) for(y=[-17,17]) translate([x,y,0])
                    cylinder(d=4.5,h=support_board_thickness+.2);
            }
        }
    }
}
module return_assembly() {
    for(i=[0:piece_count-1]) segment(i);
    for(i=[0:piece_count]) at_station(station(i)) saddle(support_offset(i));
    if(show_supports) for(i=support_stations) support(i);
}
// Sixteen bases and the two-cell Hub. Leave the two cells beside the elevator empty.
include <../common/kit_layout.scad>
module kit_reference(inset=0) {
    for(q=kit_tiles) translate([q[0]-40,q[1]-40,-tile_height+inset])
        cube([tile_size,tile_size,tile_height-2*inset]);
    translate([-80,280,-tile_height+inset]) cube([160,80,hub_height-2*inset]);
}
if(part=="segment") translate([0,0,11+piece_length(segment_index)*tan(pitch_angle)])
    segment_shape(is_curve(segment_index),piece_length(segment_index));
else if(part=="saddle") translate([0,0,14*cos(pitch_angle)+1.8])
    rotate([0,pitch_angle,0]) saddle();
else if(part=="entry_saddle") translate([0,0,14*cos(pitch_angle)+1.8+34*sin(pitch_angle)])
    rotate([0,pitch_angle,0]) saddle(34);
else if(part=="end_saddle") translate([0,0,14*cos(pitch_angle)-sin(pitch_angle)])
    rotate([0,pitch_angle,0]) saddle(-34);
else if(part=="foot") foot();
else if(part=="baseboard") support_board();
else if(part=="kit_collision") {
    // Check actual parts separately to avoid an unnecessary union of the entire assembly.
    for(i=[0:piece_count-1]) intersection() { segment(i); kit_reference(0.01); }
    for(i=[0:piece_count]) intersection() {
        at_station(station(i)) saddle(support_offset(i)); kit_reference(0.01);
    }
    for(i=support_stations) intersection() {
        support(i); kit_reference(0.01);
    }
}
else if(part=="layout") { return_assembly(); if($preview) color([0.3,0.6,0.7,0.25]) kit_reference(); }
else return_assembly();
