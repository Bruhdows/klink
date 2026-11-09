// Mechanical reference layout; power topology must be reviewed separately.
kit_tiles = concat([[-40,0],[40,0]],
    [for(y=[80:80:240]) for(x=[-120,-40,40,120]) [x,y]], [[-120,320],[120,320]]);
kit_hub_center = [0,320];
// Support-board allowance for the reference assembly, to be checked on purchase.
support_board_thickness = 12;
support_rod_underboard = 8; // washer, M6 nut and exposed thread below the board
support_board_origin = [-390,-290];
support_board_size = [700,700];
