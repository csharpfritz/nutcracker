// Nutcracker LED Matrix Enclosure Box
// Customizable 3D printable box for Raspberry Pi Zero, LED Matrix, and USB Battery
// Author: Generated for Nutcracker festive lightshow project
// Date: 2025-12-23

// === CUSTOMIZATION PARAMETERS ===
// Adjust these to fit your specific components

// LED Matrix dimensions (8x32 matrix - wider horizontal layout)
led_matrix_width = 256;     // Width in mm (32 pixels wide, ~8mm per pixel)
led_matrix_height = 64;     // Height in mm (8 pixels tall, ~8mm per pixel)
led_matrix_depth = 10;      // Depth/thickness in mm

// Raspberry Pi Zero dimensions
pi_zero_width = 65;         // Width in mm
pi_zero_length = 30;        // Length in mm
pi_zero_height = 5;         // Height/thickness in mm

// USB Battery pack dimensions (adjust for your battery)
battery_width = 60;         // Width in mm
battery_length = 90;        // Length in mm
battery_height = 15;        // Height/thickness in mm

// Box parameters
wall_thickness = 2;         // Wall thickness in mm
component_spacing = 3;      // Space between components in mm
bottom_clearance = 2;       // Space from bottom in mm
top_clearance = 2;          // Space above components in mm

// Mounting and features
mounting_hole_diameter = 3; // For screws/bolts
add_ventilation = true;     // Add ventilation slots
add_cable_channels = true;  // Add cable management channels
lid_type = "snap";          // "snap" or "screw"
display_tilt_angle = 15;    // Angle of LED matrix tilt (degrees) - plaque style

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

echo("Box outer dimensions (W x L x H):", box_width, "x", box_length, "x", box_height);
echo("Internal volume:", internal_width, "x", internal_length, "x", internal_height);

// === MAIN BOX MODULE ===
module main_box() {
    difference() {
        // Outer box
        cube([box_width, box_length, box_height]);
        
        // Hollow interior
        translate([wall_thickness, wall_thickness, wall_thickness])
            cube([internal_width, internal_length, internal_height + 1]);
        
        // USB power port access for battery (back)
        translate([wall_thickness + (internal_width - 12)/2, 
                   box_length - wall_thickness - 1, 
                   wall_thickness + bottom_clearance + 3])
            cube([12, wall_thickness + 2, 8]);
        
        // Micro USB access for Pi Zero (side)
        translate([-1, 
                   wall_thickness + component_spacing, 
                   wall_thickness + bottom_clearance + 2])
            cube([wall_thickness + 2, 10, 4]);
        
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
        
        // Mounting holes in bottom corners
        for (x = [wall_thickness + 5, box_width - wall_thickness - 5])
            for (y = [wall_thickness + 5, box_length - wall_thickness - 5])
                translate([x, y, -1])
                    cylinder(h = wall_thickness + 2, d = mounting_hole_diameter, $fn=20);
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

// === TILTED DISPLAY PLAQUE MODULE ===
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

// For printing - all parts laid flat
main_box();

translate([box_width + 10, 0, 0])
    lid();

translate([box_width/2 - (led_matrix_width + wall_thickness * 2 + component_spacing * 2)/2, 
           box_length + 20, 
           0])
    rotate([-display_tilt_angle, 0, 0])
        display_plaque();

// For assembly preview, uncomment below and comment above
// main_box();
// translate([0, 0, box_height])
//     lid();
// // Display plaque mounted on front
// translate([box_width/2 - (led_matrix_width + wall_thickness * 2 + component_spacing * 2)/2, 
//            -plaque_depth, 
//            box_height])
//     display_plaque();
