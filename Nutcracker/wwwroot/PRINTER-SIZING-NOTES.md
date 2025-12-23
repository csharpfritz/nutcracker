# Flashforge AD5X Printer Sizing Notes

## Build Volume: 220 x 220 x 220mm

## Important Measurements

### Your 8x32 LED Matrix
**CRITICAL:** Measure your actual LED matrix before printing!

Common 8x32 matrices come in different physical sizes:
- **Flexible/Bendable strips**: Can be arranged to fit
- **Rigid panel**: May be 250-260mm wide (TOO LARGE for AD5X)
- **4x (8x8) panels**: Each panel ~65mm, total ~260mm if linear
- **Segmented design**: Multiple smaller panels that can be arranged

### Current Settings (ADJUST THESE!)
The OpenSCAD file is currently set to:
- `led_matrix_width = 200mm` (safe for AD5X - 220mm limit)
- `led_matrix_height = 50mm`

### What to Measure on Your Matrix
1. **Overall width** (longest dimension)
2. **Overall height** (shorter dimension)
3. **Thickness/depth** of the PCB
4. **Check if flexible** - can it be bent/arranged in a curve?

### If Your Matrix is Too Wide (>220mm)

**Option 1: Split Display Plaque**
- Design can be modified to print plaque in 2-3 sections
- Use alignment pins and glue to join

**Option 2: Curved/Angled Arrangement**
- If matrix is flexible, arrange in slight curve or angle
- Reduces effective width

**Option 3: Vertical Orientation**
- Mount 8x32 vertically (32 pixels tall, 8 wide)
- Makes plaque narrower but taller

### Recommended Steps
1. Measure your actual matrix dimensions
2. Update parameters at top of .scad file:
   ```
   led_matrix_width = YOUR_MEASUREMENT;
   led_matrix_height = YOUR_MEASUREMENT;
   ```
3. Open in OpenSCAD and check console output
4. Verify all three pieces fit in 220x220mm area
5. Print!

### Print Settings Recommendations
- **Layer height**: 0.2mm (good balance of speed/quality)
- **Wall thickness**: 3-4 walls (for strength)
- **Infill**: 15-20% (adequate for this application)
- **Supports**: Minimal - design is mostly support-free
- **Print order**: Box first, then lid, then plaque
