// EMERGENCY MINIMAL PLATFORM BASE
// Simple flat platform to mount nutcracker
// WITH ANGLED FRONT LEDGE for LED plaque mounting
// Layout: Gift Box (left) | Nutcracker (center) | Pi 3B (right) | Battery (front)

platform_width = 200;      // ~8 inches (scaled to fit 220mm bed)
platform_length = 200;     // ~8 inches square  
platform_thickness = 5;    // Sturdy base

// LED Plaque mounting - SIMPLE VERTICAL SLOT
add_plaque_slot = true;
plaque_thickness_actual = 3;   // Plaque is 3mm thick
slot_width = 4;                // 4mm wide slot (holds 3mm plaque with clearance)
slot_depth = 15;               // How deep into platform edge
slot_height = 95;              // Height of slot opening (plaque is 90mm tall)
buildup_height = 50;           // Small ramp height (2 inches)
buildup_angle = 8;             // Degrees tilt

// Wire pass-through tunnel (RIGHT SIDE near Pi)
wire_tunnel_diameter = 12.7;   // 1/2 inch (12.7mm)
wire_tunnel_x = platform_width - 40;  // RIGHT side, near Pi
wire_tunnel_z = 8;             // Near bottom of angled wall

// Nutcracker mounting - CENTER of platform
nutcracker_mount_x = platform_width / 2;   // CENTER (100mm)
nutcracker_mount_y = platform_length / 2;  // CENTER (100mm)
nutcracker_mount_spacing_x = 50;  // 50mm spacing (fits 2.75" base)
nutcracker_mount_spacing_y = 60;  // 60mm spacing (fits 2.8125" base)
// Nutcracker holes at: (75,70), (125,70), (75,130), (125,130)
nutcracker_hole_diameter = 4;     // M4 screws

// Pi 3B mounting - RIGHT FRONT (away from LED backing!)
add_pi_mount = true;
pi_mount_x = platform_width - 35;  // FAR RIGHT, 35mm from edge
pi_mount_y = 80;  // FRONT area (was 145mm - moved to FRONT!)
pi_standoff_height = 5;    // 5mm standoffs
pi_mount_hole_diameter = 2.7;  // M2.5 screws
// Pi 3B hole spacing: ROTATED 90° - 49mm x 58mm (was 58mm x 49mm)
pi_spacing_x = 49;  // SWAPPED (rotated 90°)
pi_spacing_y = 58;  // SWAPPED (rotated 90°)
// Pi posts at: (140,51), (189,51), (140,109), (189,109) - FRONT RIGHT, clear of everything!

// Gift box mounting - LEFT side of nutcracker
add_giftbox_mount = true;
giftbox_mount_x = 40;  // FAR LEFT side
giftbox_mount_y = platform_length / 2;  // Centered with nutcracker
giftbox_mount_spacing = 40;    // 40mm x 40mm pattern
giftbox_hole_diameter = 3;     // M3 screws

// Battery area - FRONT (between nutcracker and LED panel)
// Battery: 2.75" x 4.5" x 0.625" (70mm x 114mm x 16mm)
// No screw holes - use velcro or friction fit
// Just mark the area (no mounting features)

// Optional: Platform mounting holes (to bolt to table/board)
platform_mount_holes = true;
platform_mount_hole_diameter = 5;

echo("=== PLATFORM BASE - NEW LAYOUT ===");
echo("Platform size:", platform_width, "x", platform_length, "x", platform_thickness);
echo("Layout: Gift Box (LEFT) | Nutcracker (CENTER) | Pi 3B (RIGHT)");
echo("Battery area: FRONT between nutcracker and LED panel (use velcro)");
echo("Gift box mount: ", add_giftbox_mount ? "YES - 4 mounting holes" : "NO");
echo("Fits Flashforge AD5X:", platform_width <= 220 && platform_length <= 220 ? "YES" : "NO - TOO LARGE");

module platform_base() {
    difference() {
        union() {
            // Main platform
            cube([platform_width, platform_length, platform_thickness]);
            
            // Angled backing piece with TOP overlap for plaque (slide in from side!)
            if (add_plaque_slot) {
                // Backing piece dimensions - MATCHES plaque size!
                backing_width = 200;      // Fits within platform
                backing_height = 95;      // Just taller than 90mm plaque
                backing_thickness = 3;    // Thin backing wall
                top_overlap_depth = 10;   // How far top wraps over front (holds plaque)
                top_overlap_height = 15;  // Thicker lip to grab plaque better
                
                // Position at BACK of platform, angled FORWARD
                translate([(platform_width - backing_width)/2, 
                           platform_length - 25,  // Near back edge
                           platform_thickness]) {
                    rotate([buildup_angle, 0, 0]) {  // Positive angle - tips FORWARD
                        // Back wall (plaque leans against this)
                        cube([backing_width, 
                              backing_thickness, 
                              backing_height]);
                        
                        // Top overlap piece (wraps over front to hold plaque)
                        // Positioned to catch top edge of plaque
                        translate([0, 0, backing_height - top_overlap_height])
                            cube([backing_width, 
                                  top_overlap_depth, 
                                  top_overlap_height]);
                    }
                }
            }
            
            // Pi 3B mounting standoffs (RIGHT side)
            if (add_pi_mount) {
                // Pi 3B hole pattern: 58mm x 49mm
                translate([pi_mount_x - pi_spacing_x/2, 
                           pi_mount_y - pi_spacing_y/2, 
                           platform_thickness])
                    cylinder(h = pi_standoff_height, d = 6, $fn=20);
                translate([pi_mount_x + pi_spacing_x/2, 
                           pi_mount_y - pi_spacing_y/2, 
                           platform_thickness])
                    cylinder(h = pi_standoff_height, d = 6, $fn=20);
                translate([pi_mount_x - pi_spacing_x/2, 
                           pi_mount_y + pi_spacing_y/2, 
                           platform_thickness])
                    cylinder(h = pi_standoff_height, d = 6, $fn=20);
                translate([pi_mount_x + pi_spacing_x/2, 
                           pi_mount_y + pi_spacing_y/2, 
                           platform_thickness])
                    cylinder(h = pi_standoff_height, d = 6, $fn=20);
            }
        }
        
        // Nutcracker mounting holes (CENTER)
        translate([nutcracker_mount_x - nutcracker_mount_spacing_x/2,
                   nutcracker_mount_y - nutcracker_mount_spacing_y/2,
                   -1])
            cylinder(h = platform_thickness + 2, d = nutcracker_hole_diameter, $fn=20);
        translate([nutcracker_mount_x + nutcracker_mount_spacing_x/2,
                   nutcracker_mount_y - nutcracker_mount_spacing_y/2,
                   -1])
            cylinder(h = platform_thickness + 2, d = nutcracker_hole_diameter, $fn=20);
        translate([nutcracker_mount_x - nutcracker_mount_spacing_x/2,
                   nutcracker_mount_y + nutcracker_mount_spacing_y/2,
                   -1])
            cylinder(h = platform_thickness + 2, d = nutcracker_hole_diameter, $fn=20);
        translate([nutcracker_mount_x + nutcracker_mount_spacing_x/2,
                   nutcracker_mount_y + nutcracker_mount_spacing_y/2,
                   -1])
            cylinder(h = platform_thickness + 2, d = nutcracker_hole_diameter, $fn=20);
        
        // Pi 3B mounting screw holes (through standoffs on RIGHT)
        if (add_pi_mount) {
            translate([pi_mount_x - pi_spacing_x/2, 
                       pi_mount_y - pi_spacing_y/2, 
                       platform_thickness - 1])
                cylinder(h = pi_standoff_height + 2, d = pi_mount_hole_diameter, $fn=20);
            translate([pi_mount_x + pi_spacing_x/2, 
                       pi_mount_y - pi_spacing_y/2, 
                       platform_thickness - 1])
                cylinder(h = pi_standoff_height + 2, d = pi_mount_hole_diameter, $fn=20);
            translate([pi_mount_x - pi_spacing_x/2, 
                       pi_mount_y + pi_spacing_y/2, 
                       platform_thickness - 1])
                cylinder(h = pi_standoff_height + 2, d = pi_mount_hole_diameter, $fn=20);
            translate([pi_mount_x + pi_spacing_x/2, 
                       pi_mount_y + pi_spacing_y/2, 
                       platform_thickness - 1])
                cylinder(h = pi_standoff_height + 2, d = pi_mount_hole_diameter, $fn=20);
        }
        
        // Gift box mounting holes (LEFT side, 40mm x 40mm pattern)
        if (add_giftbox_mount) {
            translate([giftbox_mount_x - giftbox_mount_spacing/2,
                       giftbox_mount_y - giftbox_mount_spacing/2,
                       -1])
                cylinder(h = platform_thickness + 2, d = giftbox_hole_diameter, $fn=20);
            translate([giftbox_mount_x + giftbox_mount_spacing/2,
                       giftbox_mount_y - giftbox_mount_spacing/2,
                       -1])
                cylinder(h = platform_thickness + 2, d = giftbox_hole_diameter, $fn=20);
            translate([giftbox_mount_x - giftbox_mount_spacing/2,
                       giftbox_mount_y + giftbox_mount_spacing/2,
                       -1])
                cylinder(h = platform_thickness + 2, d = giftbox_hole_diameter, $fn=20);
            translate([giftbox_mount_x + giftbox_mount_spacing/2,
                       giftbox_mount_y + giftbox_mount_spacing/2,
                       -1])
                cylinder(h = platform_thickness + 2, d = giftbox_hole_diameter, $fn=20);
        }
        
        // Platform mounting holes in corners (to bolt to table)
        if (platform_mount_holes) {
            translate([15, 15, -1])
                cylinder(h = platform_thickness + 2, d = platform_mount_hole_diameter, $fn=20);
            translate([platform_width - 15, 15, -1])
                cylinder(h = platform_thickness + 2, d = platform_mount_hole_diameter, $fn=20);
            translate([15, platform_length - 15, -1])
                cylinder(h = platform_thickness + 2, d = platform_mount_hole_diameter, $fn=20);
            translate([platform_width - 15, platform_length - 15, -1])
                cylinder(h = platform_thickness + 2, d = platform_mount_hole_diameter, $fn=20);
        }
        
        // Wire pass-through tunnel (goes THROUGH wall from BACK to FRONT)
        // Position on RIGHT SIDE near Pi, near bottom of angled wall
        translate([wire_tunnel_x, 
                   platform_length + 10,  // Start BEHIND the platform
                   wire_tunnel_z])
            rotate([90 - buildup_angle, 0, 0])  // Point FORWARD through angled wall
                cylinder(h = 80, d = wire_tunnel_diameter, $fn=30);
    }
}

// === RENDER ===
// Platform is too big for 220x220 bed - need to split or resize
// Option: Make it smaller to fit
smaller_platform_size = 200; // Fits 220mm bed with margin

module smaller_platform() {
    scale([smaller_platform_size/platform_width, 
           smaller_platform_size/platform_length, 
           1])
        platform_base();
}

smaller_platform();
