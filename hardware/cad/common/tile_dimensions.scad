// Shared grid and PCB body contract. See docs/specifications/interfaces.md.
tile_size = 80;
tile_height = 20;
pcb_mount_spacing = 30;
pcb_mount_height = 9;
pcb_preview_size = 68;
pcb_preview_thickness = 1.6;
pcb_preview_hole_diameter = 2.5;
mount_spacing = 24;

// KiCad origin (100,100), CAD X = pcb X-100, CAD Y = 100-pcb Y.
pcb_led_centers = [[-17,23],[17,-23]];

// M2 PCB mounting: ordinary nuts, no inserts or thread-forming screws.
pcb_screw_clearance = 2.2;
pcb_nut_af = 4.3;     // 4.0mm nominal nut plus 0.3mm across-flat clearance.
pcb_nut_depth = 1.8;  // For <=1.6mm nut thickness.

// Hub PCB is elevated so USB plugs clear adjacent tiles and 5.5mm module bases.
hub_height = 42;
hub_pcb_top = 30;
hub_usb_opening_width = 20;
hub_usb_opening_height = 10;
