# Nutcracker Enclosure - Design Notes & Decisions

**Date Created:** 2025-12-23  
**Project:** Nutcracker Holiday Display  
**Designer:** AI Assistant + User Collaboration  

---

## Hardware Specifications

### Flexible LED Matrix
- **Dimensions:** 320mm (W) × 80mm (H) × 2mm (D)
- **Type:** Flexible WS2812B 8×32 matrix
- **Source:** Physical measurement from `matrix-dimensions.jpg`
- **Connectors:** 
  - 3PIN Female connector (left)
  - 3PIN Male connector (right)
  - Voltage Adding Wires (center)

### Raspberry Pi Zero
- **Dimensions:** 65mm (W) × 30mm (L) × 5mm (H)
- **Purpose:** Control system running Blazor Server app
- **GPIO:** Controls LED matrix via GPIO pins

### USB Battery Pack
- **Dimensions:** 60mm (W) × 90mm (L) × 15mm (H)
- **Purpose:** Portable power supply

### 3D Printer
- **Model:** FlashForge AD5X
- **Build Volume:** 220mm × 220mm × 220mm
- **Constraint:** This is the PRIMARY design constraint

---

## Design Decisions

### 1. Curved vs Flat Display
**DECISION:** Use curved/wraparound display design

**Reasoning:**
- Flexible matrix is 320mm wide - too wide for 220mm print bed
- Matrix is flexible, can be curved without damage
- Curved design creates more interesting "wraparound" nutcracker effect
- Better viewing angles from multiple directions

**Implementation:**
- Cylindrical curve with 120mm radius
- Arc angle: ~153 degrees (calculated from 320mm arc length)
- Chord width: ~199mm (fits within 220mm bed)
- Arc depth: ~86mm forward projection

### 2. Component Layout
**DECISION:** Separate main box and curved display

**Main Box Contains:**
- USB battery pack (bottom layer)
- Raspberry Pi Zero (stacked above battery)
- All internal electronics
- Access ports for USB power and micro USB

**Curved Display Contains:**
- Channel to hold flexible LED matrix
- Internal support ribs every ~50mm
- Wire pass-through at bottom for data cables
- Mounting base to attach to main box

### 3. Printability Strategy
**DECISION:** Three separate printable parts

**Parts:**
1. **Main Box** - 96mm × 98mm × 25mm ✅ Fits bed
2. **Lid** - 96mm × 98mm × 2mm ✅ Fits bed  
3. **Curved Display** - 199mm × 86mm × 84mm ✅ Fits bed

All parts fit within FlashForge AD5X constraints.

### 4. Assembly Method
**DECISION:** Modular snap-fit with optional screw mounting

- Lid has internal lip that fits into main box
- Curved display has mounting base that attaches to front of main box
- Can use snap-fit or screws (configurable via `lid_type` parameter)
- Wire management through dedicated pass-through holes

---

## Key Parameters (in SCAD file)

### Matrix Configuration
```openscad
led_matrix_width = 320;     // 32cm measured
led_matrix_height = 80;     // 8cm measured
led_matrix_depth = 2;       // Very thin, flexible
```

### Curve Configuration
```openscad
use_curved_display = true;  // Enable curved design
curve_radius = 120;         // Radius in mm (adjustable)
curve_segments = 60;        // Resolution for smooth curve
```

### Box Sizing
```openscad
wall_thickness = 2;         // Standard wall thickness
component_spacing = 3;      // Air gap between components
```

---

## Design Features

### Main Box
- ✅ Internal support ledges for battery and Pi Zero
- ✅ USB power port access (back wall)
- ✅ Micro USB access for Pi (side wall)
- ✅ Ventilation slots on sides
- ✅ Mounting holes in corners (3mm diameter)
- ✅ Bottom clearance for stability

### Curved Display
- ✅ Cylindrical channel to hold flexible matrix
- ✅ Internal ribs prevent matrix sagging
- ✅ Top, bottom, and side edge caps
- ✅ Wire pass-through opening (16mm wide)
- ✅ Mounting base with proper geometry
- ✅ Smooth arc using polygon generation

### Lid
- ✅ Internal lip for secure fit
- ✅ Ventilation hole pattern
- ✅ Optional screw mounting holes
- ✅ Thin profile (2mm + 3mm lip)

---

## Potential Adjustments Before Printing

### If Curve Is Too Tight/Loose
Adjust `curve_radius` parameter:
- **Smaller radius** (e.g., 100mm) = tighter curve, narrower width, MORE curved
- **Larger radius** (e.g., 150mm) = gentler curve, wider width, LESS curved
- **Current:** 120mm provides good balance

### If Parts Don't Fit Bed
- All parts currently fit within 220mm constraint
- If issues arise, can split curved display vertically into two halves

### If Matrix Doesn't Stay in Channel
- Increase internal support ribs (change spacing from 50mm to 30mm)
- Add friction strips or texture to channel surface
- Adjust `led_matrix_depth` if matrix is thicker than 2mm

### If Need Different Viewing Angle
- Original design had `display_tilt_angle = 15°` for flat plaque
- Curved design naturally provides viewing angle range
- Can modify curve center position if needed

---

## Assembly Notes

### Order of Assembly
1. Print all three parts
2. Install battery pack in main box (bottom)
3. Install Raspberry Pi Zero above battery
4. Route power cables through internal space
5. Attach lid to main box (snap or screw)
6. Insert flexible matrix into curved display channel
7. Route data cables from Pi through wire pass-through
8. Attach curved display to front of main box

### Connection Points
- **Power:** USB battery → Pi Zero via micro USB
- **Data:** Pi Zero GPIO → LED matrix 3PIN connector
- **Wiring Route:** Through wire pass-through at bottom of curved display

---

## Files Reference

- **3D Model:** `Nutcracker\wwwroot\nutcracker-enclosure.scad`
- **Matrix Specs:** `matrix-dimensions.jpg`
- **This Document:** `Nutcracker\wwwroot\ENCLOSURE-DESIGN-NOTES.md`

---

## Future Considerations

### Possible Enhancements
- Add diffuser panel in front of LEDs for better light blending
- Create mounting brackets to attach to nutcracker figure
- Add handle or hanging loop for portability
- Design cable management clips inside main box
- Add power switch cutout if battery doesn't have external switch

### Testing Recommendations
1. Print curved display first to test matrix fit
2. Test fit matrix in channel before printing other parts
3. Verify wire routing before final assembly
4. Check that all access ports align with actual hardware

---

## Questions to Resolve Before Printing

- [ ] Is the curve radius (120mm) acceptable? Want more/less curve?
- [ ] Do you want screw mounting or snap-fit? (Currently set to snap)
- [ ] Need any specific mounting features for attaching to nutcracker?
- [ ] Want a diffuser panel in front of LEDs?
- [ ] Need power switch access cutout?
- [ ] Any specific cable routing requirements?

---

## OpenSCAD Rendering Instructions

### For Print Layout (current setting)
All parts laid flat, ready for slicing:
```openscad
main_box();
translate([box_width + 10, 0, 0]) lid();
translate([110, box_length + 60, 0]) curved_display();
```

### For Assembly Preview
To see how parts fit together, comment out print layout and uncomment:
```openscad
// main_box();
// translate([0, 0, box_height]) lid();
// translate([box_width/2, -curve_arc_depth, box_height]) curved_display();
```

---

**Status:** Design complete, ready for review before printing  
**Next Step:** Review this document, ask questions, make adjustments as needed
