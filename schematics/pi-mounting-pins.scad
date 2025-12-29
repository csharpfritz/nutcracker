// Raspberry Pi 3B Mounting Pins
// Push-fit pins to secure Pi to mounting posts
// No screws needed!

// === PARAMETERS ===
post_diameter = 2.5;        // Diameter of post on base (M2.5 screw hole size)
pin_shaft_diameter = 2.3;   // Slightly smaller for tight fit in post
pin_length = 12;            // Length to go through Pi board (2.5mm) + post height
head_diameter = 5;          // Larger head to hold Pi down
head_height = 2;            // Thin head above Pi board
taper_length = 3;           // Tapered tip for easy insertion

$fn = 32;

module mounting_pin() {
    union() {
        // Head (sits on top of Pi)
        cylinder(d=head_diameter, h=head_height);
        
        // Shaft (goes through Pi hole and into post)
        translate([0, 0, -pin_length])
            cylinder(d=pin_shaft_diameter, h=pin_length);
        
        // Tapered tip for easy insertion
        translate([0, 0, -pin_length])
            cylinder(d1=1.5, d2=pin_shaft_diameter, h=taper_length);
    }
}

// Generate 4 pins laid out for printing
for (i = [0:3]) {
    translate([i * 10, 0, 0])
        mounting_pin();
}
