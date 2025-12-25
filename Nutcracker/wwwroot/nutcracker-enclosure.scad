// Nutcracker LED Matrix Enclosure Box
// Customizable 3D printable box for Raspberry Pi Zero, LED Matrix, and USB Battery
// Author: Generated for Nutcracker festive lightshow project
// Date: 2025-12-23

// === CUSTOMIZATION PARAMETERS ===
// Adjust these to fit your specific components

// LED Matrix dimensions (Flexible 8x32 matrix)
// Actual dimensions: 320mm (32cm) x 80mm (8cm)
led_matrix_width = 320;     // Width in mm (32cm / 12.6 inch)
led_matrix_height = 80;     // Height in mm (8cm / 3.15 inch)
led_matrix_depth = 2;       // Depth/thickness in mm (flexible, very thin)

// Raspberry Pi 3B dimensions
pi_zero_width = 85;         // Width in mm (Pi 3B is larger)
pi_zero_length = 56;        // Length in mm
pi_zero_height = 17;        // Height/thickness in mm (with components)

// USB Battery pack dimensions (2 3/4 x 4 1/2 x 5/8 inches)
battery_width = 70;         // Width in mm (2.75 in = 69.8mm)
battery_length = 115;       // Length in mm (4.5 in = 114.3mm)
battery_height = 16;        // Height/thickness in mm (5/8 in = 15.9mm)

// Box parameters
wall_thickness = 2;         // Wall thickness in mm
component_spacing = 3;      // Space between components in mm
bottom_clearance = 2;       // Space from bottom in mm
top_clearance = 2;          // Space above components in mm

// Mounting and features
mounting_hole_diameter = 3; // For screws/bolts
add_ventilation = true;     // Add ventilation slots
add_cable_channels = true;  // Add cable management channels
lid_type = "screw";         // "snap" or "screw" - SCREW for easy battery access
display_tilt_angle = 15;    // Angle of LED matrix tilt (degrees) - plaque style

// Nutcracker mounting holes (to mount nutcracker to box)
nutcracker_mount_hole_spacing_x = 50; // Horizontal spacing between mounting holes
nutcracker_mount_hole_spacing_y = 60; // Vertical spacing (adjusted for 71.4mm nutcracker base)
nutcracker_mount_hole_diameter = 4;   // Diameter for nutcracker mounting screws

// Pi mounting holes (Pi 3B standard mounting)
pi_mount_hole_diameter = 2.75;        // M2.5 screw holes
pi_standoff_height = 5;               // Height of mounting standoffs

// Battery access
battery_access_cutout = true;         // Add large cutout in lid for battery access

// Curved display parameters (for flexible matrix)
use_curved_display = true;  // Use cylindrical curve instead of flat plaque
curve_radius = 120;         // Radius of curve in mm (smaller = tighter curve)
curve_segments = 60;        // Resolution of curve (higher = smoother)
split_curved_display = true; // Split curved display into 2 printable halves
alignment_pin_diameter = 3;  // Diameter of alignment pins for joining halves
use_removable_cover = true;  // Use removable clear cover instead of fixed clips (for connectors on back)

// === CALCULATED DIMENSIONS ===
// Main box holds battery and Pi Zero
internal_width = max(battery_width, pi_zero_width) + component_spacing * 2;
internal_length = battery_length + component_spacing * 2;
internal_height = max(battery_height, pi_zero_height) + component_spacing + bottom_clearance + top_clearance;

box_width = internal_width + wall_thickness * 2;
box_length = internal_length + wall_thickness * 2;
box_height = internal_height + wall_thickness;

// Display plaque dimensions (tilted front section)
plaque_depth = 25; // How far the plaque extends forward
plaque_tilt_extra = led_matrix_height * sin(display_tilt_angle); // Additional height from tilt

// Curved display calculations
curve_angle = (led_matrix_width / curve_radius) * (180 / PI); // Arc angle in degrees
curve_chord_width = 2 * curve_radius * sin(curve_angle / 2); // Straight-line width of curved display
curve_arc_depth = curve_radius * (1 - cos(curve_angle / 2)); // How far curve extends forward

echo("Box outer dimensions (W x L x H):", box_width, "x", box_length, "x", box_height);
echo("Internal volume:", internal_width, "x", internal_length, "x", internal_height);
if (use_curved_display) {
    echo("=== CURVED DISPLAY INFO ===");
    echo("Matrix arc length:", led_matrix_width, "mm");
    echo("Curve radius:", curve_radius, "mm");
    echo("Curve angle:", curve_angle, "degrees");
    echo("Display chord width:", curve_chord_width, "mm");
    echo("Display arc depth:", curve_arc_depth, "mm");
} else {
    echo("Display plaque dimensions (W x D x H):", led_matrix_width + wall_thickness * 2 + component_spacing * 2, "x", plaque_depth, "x", led_matrix_height + wall_thickness * 2);
}
echo("*** FLASHFORGE AD5X BUILD VOLUME CHECK (220x220x220mm) ***");
echo("Main box fits:", box_width <= 220 && box_length <= 220 && box_height <= 220 ? "YES" : "NO - TOO LARGE!");
echo("Lid fits:", box_width <= 220 && box_length <= 220 ? "YES" : "NO - TOO LARGE!");
if (use_curved_display) {
    echo("Curved display fits:", curve_chord_width <= 220 && curve_arc_depth <= 220 && (led_matrix_height + wall_thickness * 2) <= 220 ? "YES" : "NO - TOO LARGE!");
} else {
    echo("Plaque fits:", (led_matrix_width + wall_thickness * 2 + component_spacing * 2) <= 220 && plaque_depth <= 220 ? "YES" : "NO - TOO LARGE!");
}

// === MAIN BOX MODULE ===
module main_box() {
    difference() {
        union() {
            // Outer box
            cube([box_width, box_length, box_height]);
            
            // Pi mounting standoffs
            pi_x_offset = wall_thickness + component_spacing;
            pi_y_offset = wall_thickness + component_spacing;
            // Pi 3B mounting holes (58mm x 49mm pattern)
            translate([pi_x_offset + 3.5, pi_y_offset + 3.5, wall_thickness])
                cylinder(h = pi_standoff_height, d = 6, $fn=20);
            translate([pi_x_offset + 3.5 + 58, pi_y_offset + 3.5, wall_thickness])
                cylinder(h = pi_standoff_height, d = 6, $fn=20);
            translate([pi_x_offset + 3.5, pi_y_offset + 3.5 + 49, wall_thickness])
                cylinder(h = pi_standoff_height, d = 6, $fn=20);
            translate([pi_x_offset + 3.5 + 58, pi_y_offset + 3.5 + 49, wall_thickness])
                cylinder(h = pi_standoff_height, d = 6, $fn=20);
        }
        
        // Hollow interior
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([internal_width, internal_length, internal_height + 1]);
        
        // Pi mounting screw holes
        pi_x_offset = wall_thickness + component_spacing;
        pi_y_offset = wall_thickness + component_spacing;
        translate([pi_x_offset + 3.5, pi_y_offset + 3.5, wall_thickness - 1])
            cylinder(h = pi_standoff_height + 2, d = pi_mount_hole_diameter, $fn=20);
        translate([pi_x_offset + 3.5 + 58, pi_y_offset + 3.5, wall_thickness - 1])
            cylinder(h = pi_standoff_height + 2, d = pi_mount_hole_diameter, $fn=20);
        translate([pi_x_offset + 3.5, pi_y_offset + 3.5 + 49, wall_thickness - 1])
            cylinder(h = pi_standoff_height + 2, d = pi_mount_hole_diameter, $fn=20);
        translate([pi_x_offset + 3.5 + 58, pi_y_offset + 3.5 + 49, wall_thickness - 1])
            cylinder(h = pi_standoff_height + 2, d = pi_mount_hole_diameter, $fn=20);
        
        // Nutcracker mounting holes (on top of box, centered)
        translate([box_width/2 - nutcracker_mount_hole_spacing_x/2, 
                   box_length/2 - nutcracker_mount_hole_spacing_y/2, 
                   -1])
            cylinder(h = wall_thickness + 2, d = nutcracker_mount_hole_diameter, $fn=20);
        translate([box_width/2 + nutcracker_mount_hole_spacing_x/2, 
                   box_length/2 - nutcracker_mount_hole_spacing_y/2, 
                   -1])
            cylinder(h = wall_thickness + 2, d = nutcracker_mount_hole_diameter, $fn=20);
        translate([box_width/2 - nutcracker_mount_hole_spacing_x/2, 
                   box_length/2 + nutcracker_mount_hole_spacing_y/2, 
                   -1])
            cylinder(h = wall_thickness + 2, d = nutcracker_mount_hole_diameter, $fn=20);
        translate([box_width/2 + nutcracker_mount_hole_spacing_x/2, 
                   box_length/2 + nutcracker_mount_hole_spacing_y/2, 
                   -1])
            cylinder(h = wall_thickness + 2, d = nutcracker_mount_hole_diameter, $fn=20);
        
        // USB power port access for battery (back)
        translate([wall_thickness + (internal_width - 12)/2, 
                   box_length - wall_thickness - 1, 
                   wall_thickness + bottom_clearance + 3])
            cube([12, wall_thickness + 2, 8]);
        
        // USB/Ethernet access for Pi 3B (side)
        translate([-1, 
                   wall_thickness + component_spacing + 10, 
                   wall_thickness + bottom_clearance + pi_standoff_height + 2])
            cube([wall_thickness + 2, 35, 15]);
        
        // LED wire pass-through hole (front, near display connection)
        translate([box_width/2 - 8, 
                   -1, 
                   wall_thickness + bottom_clearance + pi_standoff_height + 5])
            cube([16, wall_thickness + 2, 10]);
        
        // Display mounting screw holes (M3 screws from inside box)
        // These align with the curved display mounting tabs
        display_mount_hole_spacing = 60; // Distance between mounting holes
        translate([box_width/2 - display_mount_hole_spacing/2, 
                   wall_thickness - 1, 
                   box_height - 5])
            cylinder(h = wall_thickness + 2, d = 3.2, $fn=20);
        translate([box_width/2 + display_mount_hole_spacing/2, 
                   wall_thickness - 1, 
                   box_height - 5])
            cylinder(h = wall_thickness + 2, d = 3.2, $fn=20);
        
        // Ventilation slots (sides)
        if (add_ventilation) {
            for (i = [0:3]) {
                // Right side
                translate([box_width - wall_thickness - 1, 
                           wall_thickness + 10 + i * 20, 
                           wall_thickness + 5])
                    cube([wall_thickness + 2, 12, 3]);
            }
        }
        
        // Mounting holes in bottom corners (for lid screws)
        if (lid_type == "screw") {
            for (x = [wall_thickness + 5, box_width - wall_thickness - 5])
                for (y = [wall_thickness + 5, box_length - wall_thickness - 5])
                    translate([x, y, -1])
                        cylinder(h = wall_thickness + 2, d = mounting_hole_diameter, $fn=20);
        }
    }
    
    // Internal component supports
    // Battery support ledge (bottom)
    translate([wall_thickness + component_spacing, 
               wall_thickness + component_spacing, 
               wall_thickness])
        cube([battery_width, battery_length, 1]);
    
    // Pi Zero support ledge (stacked above or beside battery)
    translate([wall_thickness + component_spacing, 
               wall_thickness + component_spacing, 
               wall_thickness + battery_height + component_spacing])
        cube([pi_zero_width, pi_zero_length, 1]);
}

// === CURVED DISPLAY MODULE (for flexible matrix) ===
// Alignment pin post for joining halves
module alignment_pin_post(height=10) {
    cylinder(h = height, d = alignment_pin_diameter + 1, $fn=20);
}

// Alignment pin hole for joining halves
module alignment_pin_hole(depth=12) {
    cylinder(h = depth, d = alignment_pin_diameter + 0.3, $fn=20);
}

// Half of curved display (left or right)
module curved_display_half(is_left=true) {
    intersection() {
        curved_display();
        
        // Cut plane - keep left or right half
        translate([is_left ? -200 : 0, -100, -10])
            cube([200, 300, 200]);
    }
    
    // Add alignment pins/holes at split line
    pin_y_positions = [-40, 0, 40];
    for (y_pos = pin_y_positions) {
        if (is_left) {
            // Left half gets posts
            translate([0, y_pos, led_matrix_height/2])
                rotate([0, 90, 0])
                    alignment_pin_post(height=8);
        } else {
            // Right half gets holes
            translate([0, y_pos, led_matrix_height/2])
                rotate([0, 90, 0])
                    translate([0, 0, -1])
                        alignment_pin_hole(depth=10);
        }
    }
}

module curved_display() {
    matrix_channel_depth = led_matrix_depth + 1; // Channel to hold flexible matrix
    total_height = led_matrix_height + wall_thickness * 2;
    clip_depth = 1.5; // How far clips overlap the matrix
    
    difference() {
        union() {
            // Curved back panel (matrix mounts to this)
            rotate([90, 0, 0])
            rotate([0, 0, 90])
            linear_extrude(height = total_height, center = false)
                arc_segment(curve_radius + wall_thickness/2, curve_angle, curve_segments);
            
            // Top edge frame
            translate([0, 0, total_height - wall_thickness])
            rotate([90, 0, 0])
            rotate([0, 0, 90])
            linear_extrude(height = wall_thickness)
                difference() {
                    arc_segment(curve_radius + wall_thickness + 3, curve_angle, curve_segments);
                    arc_segment(curve_radius - 2, curve_angle, curve_segments);
                }
            
            // Bottom edge frame
            rotate([90, 0, 0])
            rotate([0, 0, 90])
            linear_extrude(height = wall_thickness)
                difference() {
                    arc_segment(curve_radius + wall_thickness + 3, curve_angle, curve_segments);
                    arc_segment(curve_radius - 2, curve_angle, curve_segments);
                }
            
            // Side caps
            for (side = [0, 1]) {
                mirror([side, 0, 0])
                translate([curve_chord_width/2, -(curve_radius + wall_thickness) * cos(curve_angle/2), 0])
                rotate([0, 0, 90 - curve_angle/2])
                cube([wall_thickness, wall_thickness, total_height]);
            }
            
            // Mounting base
            translate([-curve_chord_width/2 - wall_thickness, -curve_arc_depth - wall_thickness, -wall_thickness])
                cube([curve_chord_width + wall_thickness * 2, wall_thickness * 2, wall_thickness]);
            
            // Mounting tabs with screw holes
            for (x = [-curve_chord_width/4, curve_chord_width/4]) {
                translate([x - 6, -curve_arc_depth - wall_thickness, -wall_thickness])
                    cube([12, wall_thickness * 2, wall_thickness + 3]);
            }
        }
        
        // Mounting screw holes in tabs (M3 screws)
        for (x = [-curve_chord_width/4, curve_chord_width/4]) {
            translate([x, -curve_arc_depth, -wall_thickness - 1])
                cylinder(h = wall_thickness + 5, d = 3.2, $fn=20);
        }
        
        // Wire pass-through holes at bottom
        translate([-8, -curve_arc_depth - wall_thickness - 1, -wall_thickness - 1])
            cube([16, wall_thickness + 2, wall_thickness + 2]);
    }
    
    // Internal support ribs for matrix (every ~50mm along arc)
    num_ribs = floor(led_matrix_width / 50);
    for (i = [1 : num_ribs - 1]) {
        rib_angle = -curve_angle/2 + (i * curve_angle / num_ribs);
        rotate([0, 0, rib_angle])
        translate([0, -curve_radius - wall_thickness/2, wall_thickness])
            cube([0.8, wall_thickness, led_matrix_height]);
    }
}

// === REMOVABLE CLEAR COVER FOR LED MATRIX ===
module matrix_cover() {
    total_height = led_matrix_height + wall_thickness * 2;
    cover_thickness = 1.5;
    
    difference() {
        union() {
            // Curved clear front panel
            rotate([90, 0, 0])
            rotate([0, 0, 90])
            linear_extrude(height = total_height - wall_thickness * 2, center = false)
                arc_segment(curve_radius + wall_thickness + 2, curve_angle, curve_segments);
            
            // Top clip tabs (snap into frame)
            num_clips = 4;
            for (i = [0 : num_clips - 1]) {
                clip_angle = -curve_angle/2 + ((i + 0.5) * curve_angle / num_clips);
                rotate([0, 0, clip_angle])
                translate([-1.5, -curve_radius - wall_thickness - 3.5, total_height - wall_thickness - 0.5])
                    cube([3, 1, 2]);
            }
            
            // Bottom clip tabs
            for (i = [0 : num_clips - 1]) {
                clip_angle = -curve_angle/2 + ((i + 0.5) * curve_angle / num_clips);
                rotate([0, 0, clip_angle])
                translate([-1.5, -curve_radius - wall_thickness - 3.5, wall_thickness - 1.5])
                    cube([3, 1, 2]);
            }
        }
    }
}

// Helper module to create arc segment
module arc_segment(radius, angle, segments) {
    step_angle = angle / segments;
    points = concat(
        [[0, 0]],
        [for (i = [0:segments]) 
            [radius * cos(-angle/2 + i * step_angle), 
             radius * sin(-angle/2 + i * step_angle)]
        ]
    );
    polygon(points);
}

// === FLAT DISPLAY PLAQUE MODULE (original - kept for reference) ===
module display_plaque() {
    plaque_width = led_matrix_width + wall_thickness * 2 + component_spacing * 2;
    plaque_height_base = led_matrix_height * cos(display_tilt_angle) + wall_thickness * 2;
    
    difference() {
        union() {
            // Main angled plaque body
            rotate([display_tilt_angle, 0, 0])
            translate([0, 0, 0])
            difference() {
                cube([plaque_width, plaque_depth, led_matrix_height + wall_thickness * 2]);
                
                // Hollow out back for LED matrix
                translate([wall_thickness + component_spacing, 
                           wall_thickness, 
                           wall_thickness])
                    cube([led_matrix_width, plaque_depth, led_matrix_height + 1]);
            }
            
            // Base connection to main box
            translate([0, 0, -wall_thickness])
                cube([plaque_width, wall_thickness + 2, wall_thickness]);
        }
        
        // LED Matrix viewing window
        rotate([display_tilt_angle, 0, 0])
        translate([wall_thickness + component_spacing, 
                   -1, 
                   wall_thickness])
            cube([led_matrix_width, wall_thickness + 2, led_matrix_height]);
        
        // Wire pass-through hole at bottom
        translate([plaque_width/2 - 5, 
                   -1, 
                   -wall_thickness - 1])
            cube([10, wall_thickness + 3, wall_thickness + 2]);
    }
    
    // LED Matrix support clips inside plaque
    clip_thickness = 1.5;
    clip_height = 3;
    rotate([display_tilt_angle, 0, 0]) {
        // Left clip
        translate([wall_thickness + component_spacing - clip_thickness, 
                   wall_thickness + 2, 
                   wall_thickness])
            cube([clip_thickness, led_matrix_depth - 4, clip_height]);
        
        // Right clip
        translate([wall_thickness + component_spacing + led_matrix_width, 
                   wall_thickness + 2, 
                   wall_thickness])
            cube([clip_thickness, led_matrix_depth - 4, clip_height]);
    }
}

// === LID MODULE ===
module lid() {
    difference() {
        union() {
            // Main lid plate
            cube([box_width, box_length, wall_thickness]);
            
            // Lip that fits inside box
            translate([wall_thickness + 0.2, wall_thickness + 0.2, wall_thickness])
                cube([internal_width - 0.4, internal_length - 0.4, 3]);
        }
        
        // Mounting holes for screws (if screw type)
        if (lid_type == "screw") {
            for (x = [wall_thickness + 5, box_width - wall_thickness - 5])
                for (y = [wall_thickness + 5, box_length - wall_thickness - 5])
                    translate([x, y, -1])
                        cylinder(h = wall_thickness + 2, d = mounting_hole_diameter + 0.5, $fn=20);
        }
        
        // Battery access cutout (large opening for connecting wires)
        if (battery_access_cutout) {
            translate([wall_thickness + component_spacing + 5, 
                       wall_thickness + component_spacing + 5, 
                       -1])
                cube([battery_width - 10, battery_length - 10, wall_thickness + 2]);
        }
        
        // Ventilation holes in lid
        for (x = [0:3])
            for (y = [0:4])
                translate([box_width/2 - 20 + x * 12, 
                           box_length/2 - 25 + y * 12, 
                           -1])
                    cylinder(h = wall_thickness + 2, d = 4, $fn=20);
    }
}

// === RENDER SELECTION ===
// Comment/uncomment to choose what to render

// RENDER INDIVIDUAL PARTS (uncomment one at a time)
// Part 1: Main box only
main_box();

// Part 2: Lid only
//lid();

// Part 3: Display left half only
//if (use_curved_display && split_curved_display) {
//    curved_display_half(is_left=true);
//}

// Part 4: Display right half only
//if (use_curved_display && split_curved_display) {
//    curved_display_half(is_left=false);
//}

// Part 5: Display cover only
//if (use_curved_display && use_removable_cover) {
//    matrix_cover();
//}

// ALL PARTS TOGETHER (too big for bed!)
//main_box();
//translate([box_width + 10, 0, 0])
//    lid();
//if (use_curved_display) {
//    if (split_curved_display) {
//        translate([0, box_length + 60, 0])
//            curved_display_half(is_left=true);
//        translate([curve_chord_width/2 + 20, box_length + 60, 0])
//            curved_display_half(is_left=false);
//        if (use_removable_cover) {
//            translate([0, box_length + 160, 0])
//                matrix_cover();
//        }
//    }
//}

// For assembly preview, uncomment below and comment above
// main_box();
// translate([0, 0, box_height])
//     lid();
// if (use_curved_display) {
//     // Curved display mounted on front
//     translate([box_width/2, -curve_arc_depth, box_height])
//         curved_display();
// } else {
//     // Flat display plaque mounted on front
//     translate([box_width/2 - (led_matrix_width + wall_thickness * 2 + component_spacing * 2)/2, 
//                -plaque_depth, 
//                box_height])
//         display_plaque();
// }
