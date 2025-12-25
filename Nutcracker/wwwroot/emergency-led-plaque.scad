// EMERGENCY MINIMAL LED PLAQUE - Flat version for quick printing
// 32cm x 8cm flat backing with clips to hold WS2812B LED matrix
// Designed to mount directly to nutcracker or platform

// LED Matrix dimensions (from matrix-dimensions.jpg)
led_matrix_width = 320;     // 32cm = 320mm
led_matrix_height = 80;     // 8cm = 80mm
led_matrix_depth = 2;       // Thin flexible strip

// Plaque parameters
wall_thickness = 2;
border_width = 5;           // Border around LED matrix
clip_size = 3;              // Small clips to hold LEDs
clip_spacing = 40;          // Clip every 40mm

// Cable holes - BIGGER for connectors (1 inch = 25.4mm diameter)
cable_hole_diameter = 25.4;  // 1 inch diameter holes
// Connector positions (from matrix-dimensions.jpg)
// Left: 3PIN Female at ~40mm from left
// Center: Voltage wires at center
// Right: 3PIN Male at ~40mm from right
cable_hole_left_x = 40;      // Left connector position
cable_hole_center_x = led_matrix_width / 2;  // Center voltage wires
cable_hole_right_x = led_matrix_width - 40;  // Right connector position
cable_hole_y = led_matrix_height / 2;        // Centered vertically

// Mounting
mounting_hole_diameter = 4; // For M4 screws to attach to nutcracker
mounting_hole_spacing_x = 280; // Near edges of plaque
mounting_hole_spacing_y = 60;  // Top and bottom

plaque_width = led_matrix_width + border_width * 2;
plaque_height = led_matrix_height + border_width * 2 + 1;  // +1mm extra height
plaque_thickness = 3;

echo("=== FLAT LED PLAQUE DIMENSIONS ===");
echo("Plaque size:", plaque_width, "x", plaque_height, "x", plaque_thickness);
echo("Fits Flashforge AD5X:", plaque_width <= 220 ? "NO - NEED TO SPLIT" : "NO - NEED TO SPLIT");
echo("Will generate in 2 halves for printing");

// === MAIN PLAQUE MODULE ===
module led_plaque_half(is_left=true) {
    half_width = plaque_width / 2 + 5; // Extra for overlap
    
    difference() {
        union() {
            intersection() {
                led_plaque_full();
                
                // Cut plane
                translate([is_left ? -10 : plaque_width/2 - 5, -10, -10])
                    cube([plaque_width/2 + 15, plaque_height + 20, 20]);
            }
            
            // Left half gets PINS (add them)
            if (is_left) {
                for (y = [plaque_height/4, plaque_height/2, 3*plaque_height/4]) {
                    translate([plaque_width/2, y, plaque_thickness/2])
                        rotate([0, 90, 0])
                            cylinder(h = 8, d = 4, $fn=20);
                }
            }
        }
        
        // Right half gets HOLES (subtract them)
        if (!is_left) {
            for (y = [plaque_height/4, plaque_height/2, 3*plaque_height/4]) {
                translate([plaque_width/2 - 8, y, plaque_thickness/2])
                    rotate([0, 90, 0])
                        cylinder(h = 10, d = 4.3, $fn=20);
            }
        }
    }
}

module led_plaque_full() {
    difference() {
        union() {
            // Main plaque backing
            cube([plaque_width, plaque_height, plaque_thickness]);
            
            // Edge walls to hold LED matrix
            // Top wall
            translate([border_width, plaque_height - border_width, 0])
                cube([led_matrix_width, border_width, plaque_thickness + 2]);
            // Bottom wall
            translate([border_width, 0, 0])
                cube([led_matrix_width, border_width, plaque_thickness + 2]);
            // Left wall
            translate([0, border_width, 0])
                cube([border_width, led_matrix_height, plaque_thickness + 2]);
            // Right wall
            translate([plaque_width - border_width, border_width, 0])
                cube([border_width, led_matrix_height, plaque_thickness + 2]);
            
            // Retention clips along top and bottom edges
            num_clips = floor(led_matrix_width / clip_spacing);
            for (i = [1 : num_clips - 1]) {
                x_pos = border_width + i * clip_spacing;
                // Top clips
                translate([x_pos - clip_size/2, plaque_height - border_width - 1, plaque_thickness])
                    cube([clip_size, 1, 2]);
                // Bottom clips
                translate([x_pos - clip_size/2, border_width, plaque_thickness])
                    cube([clip_size, 1, 2]);
            }
        }
        
        // Cable holes for connectors (1 inch diameter, positioned per matrix-dimensions.jpg)
        // Left: 3PIN Female connector
        translate([border_width + cable_hole_left_x, 
                   border_width + cable_hole_y, 
                   -1])
            cylinder(h = plaque_thickness + 2, d = cable_hole_diameter, $fn=60);
        
        // Center: Voltage wires - CLEAN HOLE (no floating center)
        translate([border_width + cable_hole_center_x, 
                   border_width + cable_hole_y, 
                   -1])
            cylinder(h = plaque_thickness + 2, d = cable_hole_diameter, $fn=60);
        
        // Right: 3PIN Male connector
        translate([border_width + cable_hole_right_x, 
                   border_width + cable_hole_y, 
                   -1])
            cylinder(h = plaque_thickness + 2, d = cable_hole_diameter, $fn=60);
        
        // Mounting holes at corners
        translate([border_width + 10, border_width + 10, -1])
            cylinder(h = plaque_thickness + 2, d = mounting_hole_diameter, $fn=20);
        translate([plaque_width - border_width - 10, border_width + 10, -1])
            cylinder(h = plaque_thickness + 2, d = mounting_hole_diameter, $fn=20);
        translate([border_width + 10, plaque_height - border_width - 10, -1])
            cylinder(h = plaque_thickness + 2, d = mounting_hole_diameter, $fn=20);
        translate([plaque_width - border_width - 10, plaque_height - border_width - 10, -1])
            cylinder(h = plaque_thickness + 2, d = mounting_hole_diameter, $fn=20);
        
        // Wire pass-through hole at bottom center
        translate([plaque_width/2 - 8, -1, plaque_thickness/2 - 3])
            cube([16, border_width + 2, 6]);
    }
}

// === RENDER ===
// RENDER ONE HALF AT A TIME!
// Comment/uncomment to choose which half to render

// LEFT HALF ONLY (render this first)
////led_plaque_half(is_left=true);

// RIGHT HALF ONLY (render this second)
led_plaque_half(is_left=false);




