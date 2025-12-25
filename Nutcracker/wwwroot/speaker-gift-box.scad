// Bluetooth Speaker Gift Box Enclosure
// Festive gift-wrapped appearance with flip-top lid
// Designed for cylinder speaker: 1.75" diameter x 1.875" tall
// Red box with yellow bow/ribbon accents

// === SPEAKER PARAMETERS ===
speaker_diameter = 51;      // 2.0 inches = 50.8mm (1.75" + 0.25" clearance)
speaker_height = 48;        // 1.875 inches = 47.6mm (with clearance)

// === BOX PARAMETERS ===
wall_thickness = 2;
clearance = 5;              // Extra space around speaker (increased for print tolerance)
bottom_padding = 4;         // Space below speaker for stability
top_clearance = 4;          // Space above speaker

// Box dimensions (square box for gift aesthetic)
box_size = speaker_diameter + clearance * 2 + wall_thickness * 2;
box_height = speaker_height + bottom_padding + top_clearance + wall_thickness;

// Lid parameters
lid_height = 15;            // Height of flip-top lid
hinge_width = box_size - 8; // Width of living hinge
hinge_thickness = 0.8;      // Thin for flexibility

// Mounting holes (optional - to bolt to platform)
add_mounting_holes = true;
mounting_hole_diameter = 4;
mounting_hole_spacing = 40; // Spacing between holes

// Decorative features
add_bow = true;
add_ribbon = true;
sound_hole_pattern = "snowflake"; // "snowflake", "star", "grid"

echo("=== SPEAKER GIFT BOX DIMENSIONS ===");
echo("Box outer size:", box_size, "x", box_size, "x", box_height);
echo("Internal speaker space: Diameter", speaker_diameter, "Height", speaker_height);
echo("Flashforge AD5X check:", box_size <= 220 ? "FITS" : "TOO LARGE");

// === MAIN BOX MODULE ===
module gift_box_base() {
    difference() {
        union() {
            // Outer box
            cube([box_size, box_size, box_height]);
            
            // Hinge mounting lip on back edge
            translate([wall_thickness + 2, box_size - wall_thickness, box_height - wall_thickness])
                cube([hinge_width, wall_thickness + 2, wall_thickness + 3]);
        }
        
        // Hollow interior (cylindrical for speaker)
        translate([box_size/2, box_size/2, wall_thickness + bottom_padding])
            cylinder(h = speaker_height + top_clearance + 1, d = speaker_diameter, $fn=60);
        
        // Charging port access (front center, bottom edge)
        translate([box_size/2 - 6, -1, wall_thickness + bottom_padding + speaker_height/3])
            cube([12, wall_thickness + 2, 8]);
        
        // Button access (top side)
        translate([box_size - wall_thickness - 1, box_size/2 - 8, box_height - lid_height - 5])
            cube([wall_thickness + 2, 16, 10]);
        
        // Mounting holes in base (if enabled)
        if (add_mounting_holes) {
            translate([box_size/2 - mounting_hole_spacing/2, 
                       box_size/2 - mounting_hole_spacing/2, 
                       -1])
                cylinder(h = wall_thickness + 2, d = mounting_hole_diameter, $fn=20);
            translate([box_size/2 + mounting_hole_spacing/2, 
                       box_size/2 - mounting_hole_spacing/2, 
                       -1])
                cylinder(h = wall_thickness + 2, d = mounting_hole_diameter, $fn=20);
            translate([box_size/2 - mounting_hole_spacing/2, 
                       box_size/2 + mounting_hole_spacing/2, 
                       -1])
                cylinder(h = wall_thickness + 2, d = mounting_hole_diameter, $fn=20);
            translate([box_size/2 + mounting_hole_spacing/2, 
                       box_size/2 + mounting_hole_spacing/2, 
                       -1])
                cylinder(h = wall_thickness + 2, d = mounting_hole_diameter, $fn=20);
        }
        
        // Hinge pin holes
        translate([wall_thickness + 4, box_size + 1, box_height + 1.5])
            rotate([90, 0, 0])
                cylinder(h = wall_thickness + 4, d = 2, $fn=20);
        translate([box_size - wall_thickness - 4, box_size + 1, box_height + 1.5])
            rotate([90, 0, 0])
                cylinder(h = wall_thickness + 4, d = 2, $fn=20);
        
        // Decorative ribbon embossing (recessed stripes)
        if (add_ribbon) {
            // Front ribbon stripe (recessed)
            translate([box_size/2 - 4, -1, 0])
                cube([8, box_size + 2, 0.5]);
            
            // Side ribbon stripe (recessed, crossing)
            translate([-1, box_size/2 - 4, 0])
                cube([box_size + 2, 8, 0.5]);
        }
    }
}

// === FLIP-TOP LID MODULE ===
module gift_box_lid() {
    difference() {
        union() {
            // Main lid plate
            translate([wall_thickness, wall_thickness, 0])
                cube([box_size - wall_thickness * 2, box_size - wall_thickness * 2, wall_thickness]);
            
            // Lid walls (forms box top)
            difference() {
                cube([box_size, box_size, lid_height]);
                translate([wall_thickness, wall_thickness, -1])
                    cube([box_size - wall_thickness * 2, box_size - wall_thickness * 2, lid_height]);
            }
            
            // Living hinge strip (thin flexible plastic)
            translate([wall_thickness + 2, box_size - wall_thickness - 2, 0])
                cube([hinge_width, hinge_thickness, wall_thickness]);
            
            // Hinge pin posts
            translate([wall_thickness + 4, box_size - wall_thickness, wall_thickness/2])
                rotate([90, 0, 0])
                    cylinder(h = wall_thickness + 1, d = 3.5, $fn=20);
            translate([box_size - wall_thickness - 4, box_size - wall_thickness, wall_thickness/2])
                rotate([90, 0, 0])
                    cylinder(h = wall_thickness + 1, d = 3.5, $fn=20);
        }
        
        // Hinge pin holes
        translate([wall_thickness + 4, box_size, wall_thickness/2])
            rotate([90, 0, 0])
                cylinder(h = wall_thickness + 3, d = 2.2, $fn=20);
        translate([box_size - wall_thickness - 4, box_size, wall_thickness/2])
            rotate([90, 0, 0])
                cylinder(h = wall_thickness + 3, d = 2.2, $fn=20);
        
        // Sound holes based on pattern
        if (sound_hole_pattern == "snowflake") {
            snowflake_sound_holes();
        } else if (sound_hole_pattern == "star") {
            star_sound_holes();
        } else {
            grid_sound_holes();
        }
        
        // Decorative ribbon grooves on lid walls (recessed stripes)
        if (add_ribbon) {
            // Front ribbon stripe (vertical, recessed)
            translate([box_size/2 - 4, -1, 0])
                cube([8, wall_thickness + 1, lid_height + 1]);
            
            // Back ribbon stripe (vertical, recessed)
            translate([box_size/2 - 4, box_size - wall_thickness, 0])
                cube([8, wall_thickness + 1, lid_height + 1]);
            
            // Left side ribbon stripe (horizontal, recessed)
            translate([-1, box_size/2 - 4, 0])
                cube([wall_thickness + 1, 8, lid_height + 1]);
            
            // Right side ribbon stripe (horizontal, recessed)
            translate([box_size - wall_thickness, box_size/2 - 4, 0])
                cube([wall_thickness + 1, 8, lid_height + 1]);
        }
    }
    
    // Decorative bow on top (if enabled)
    if (add_bow) {
        translate([box_size/2, box_size/2, lid_height])
            decorative_bow();
    }
}

// === DECORATIVE BOW MODULE ===
module decorative_bow() {
    bow_size = 12;
    
    // Bow loops (two rounded rectangles)
    translate([-bow_size/2, -2, 0])
        bow_loop();
    translate([bow_size/2, -2, 0])
        mirror([1, 0, 0])
            bow_loop();
    
    // Center knot
    translate([0, 0, 2])
        sphere(d = 5, $fn=30);
    
    // Ribbon tails
    translate([-2, 2, 0])
        rotate([0, 0, 45])
            cube([4, 10, 1]);
    translate([2, 2, 0])
        rotate([0, 0, -45])
            cube([4, 10, 1]);
}

module bow_loop() {
    rotate([0, 45, 0])
        difference() {
            hull() {
                translate([0, 0, 0]) sphere(d = 6, $fn=30);
                translate([0, 8, 0]) sphere(d = 6, $fn=30);
            }
            hull() {
                translate([0, 0, 0]) sphere(d = 3, $fn=30);
                translate([0, 8, 0]) sphere(d = 3, $fn=30);
            }
        }
}

// === SOUND HOLE PATTERNS ===
module snowflake_sound_holes() {
    // Central snowflake pattern
    num_arms = 6;
    for (i = [0 : num_arms - 1]) {
        rotate([0, 0, i * 360 / num_arms])
        translate([0, 0, -1]) {
            // Main arm
            translate([box_size/2, box_size/2, 0])
                cube([2, 12, wall_thickness + 2], center=true);
            // Side branches
            translate([box_size/2, box_size/2 + 6, 0])
                rotate([0, 0, 45])
                    cube([2, 4, wall_thickness + 2], center=true);
            translate([box_size/2, box_size/2 + 6, 0])
                rotate([0, 0, -45])
                    cube([2, 4, wall_thickness + 2], center=true);
        }
    }
    // Center circle
    translate([box_size/2, box_size/2, -1])
        cylinder(h = wall_thickness + 2, d = 4, $fn=30);
}

module star_sound_holes() {
    // 5-pointed star pattern
    num_points = 5;
    for (i = [0 : num_points - 1]) {
        rotate([0, 0, i * 360 / num_points])
        translate([box_size/2, box_size/2 + 8, -1])
            cylinder(h = wall_thickness + 2, d = 3, $fn=20);
    }
    // Center
    translate([box_size/2, box_size/2, -1])
        cylinder(h = wall_thickness + 2, d = 5, $fn=30);
}

module grid_sound_holes() {
    // Simple grid of holes for sound
    hole_spacing = 8;
    for (x = [-2 : 2]) {
        for (y = [-2 : 2]) {
            translate([box_size/2 + x * hole_spacing, 
                       box_size/2 + y * hole_spacing, 
                       -1])
                cylinder(h = wall_thickness + 2, d = 4, $fn=20);
        }
    }
}

// === RENDER SELECTION ===
// For printing - box and lid laid flat

// SINGLE MERGED MODEL - For AMS multi-color printing
// Print this as one file, then paint colors in Orca Slicer
gift_box_base();

translate([box_size + 10, 0, 0])
    gift_box_lid();

// For assembly preview, uncomment below:
// gift_box_base();
// translate([0, 0, box_height])
//     rotate([0, 0, 0])
//         gift_box_lid();
