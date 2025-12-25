# Nutcracker Enclosure Hardware Shopping List

## Screws Needed from Home Depot

### 1. Lid Screws (4 needed)
- **#6 x ½" Phillips Pan Head Sheet Metal Screws** (stainless steel)
- **Purpose:** Securing the lid to the box base for battery access
- **Notes:** Thread into 3mm holes in the plastic. Self-tapping screws work best for PLA/PETG prints.

### 2. Display Mounting Screws (2 needed)
- **M3 x 10mm Phillips Pan Head Machine Screws** with nuts
- **Purpose:** Mounting the curved LED display to the front of the box
- **Notes:** Goes through display mounting tabs into the box. Install from inside the box.

### 3. Raspberry Pi Mounting Screws (4 needed)
- **M2.5 x 8mm Phillips Pan Head Screws** with nylon washers
- **Purpose:** Mounting the Raspberry Pi 3B to the standoffs inside the box
- **Notes:** Standard Pi mounting hardware. Often sold as "Raspberry Pi mounting kit" in electronics section.

### 4. Nutcracker Base Mounting Screws (4 needed)
- **M4 x 12mm or #8 x ½" Phillips Pan Head Screws** with washers
- **Purpose:** Mounting the nutcracker decoration to the top of the box
- **Notes:** 4mm holes in a 50mm x 70mm rectangular pattern. Use washers to distribute load.

## Assembly Notes

### Display Mounting Method
1. The curved LED display has a flat mounting base with two tabs
2. Tabs are positioned at ±¼ of the display width
3. M3 screws are inserted from inside the box through the front wall into the display tabs
4. Wire pass-through hole (16mm) allows LED cables to run from Pi to display

### LED Matrix Installation (No Glue Required!)
1. **Open curved backing** - The display has a curved back panel that the matrix rests against
2. **Support ribs** - Internal ribs every ~50mm provide backing support along the curve
3. **Installation:** 
   - Place the LED matrix onto the curved back panel with connectors facing outward
   - Arrange the power wires through the wire pass-through hole
   - Snap the removable clear cover over the front - it has spring clips at top and bottom edges
4. **Removable cover** - Clear curved front cover snaps on with 4 clips on each edge
5. **Connector clearance** - The open design allows the 3PIN connectors and wires on the back to exit freely
6. **Removal:** Pop off the snap-on cover to service or replace the LED matrix

### Battery Access
- Lid is secured with 4 corner screws (self-tapping sheet metal screws)
- Large cutout in lid provides direct access to battery compartment
- Remove 4 screws to access battery and connect power cables

### Hardware Pattern Summary
- **Nutcracker mounting:** 4 holes, 50mm x 60mm spacing (top of box) - **UPDATED to fit 2¾" x 2¹³⁄₁₆" nutcracker base**
- **Display mounting:** 2 holes on front wall
- **Pi mounting:** 4 holes, 58mm x 49mm standard Pi 3B pattern (inside box)
- **Lid mounting:** 4 corner holes

## Total Screw Count
- 14 screws total for nutcracker enclosure
- Optional: 4 screws for speaker gift box mounting
- Recommend buying small packs (typically 10-25 pieces per pack)
- Total cost estimate: $10-15

---

## Speaker Gift Box

A separate festive gift box enclosure for your Bluetooth speaker is included in `speaker-gift-box.scad`.

### Features:
- 🎁 **Gift-wrapped appearance** - Looks like a wrapped present!
- 🔊 **Snowflake sound holes** - Decorative pattern lets sound through
- 🎀 **3D printed bow on top** - Ornamental bow (print in yellow)
- 🎨 **Ribbon stripes** - Embossed vertical/horizontal ribbon crossing pattern
- 📱 **Flip-top lid** - Living hinge on back edge for easy access
- 🔌 **Access cutouts** - Front charging port access and side button access
- ⚙️ **Platform mounting** - Optional 4 holes to bolt to platform (40mm spacing)

### Dimensions:
- Box: 56mm x 56mm x 66mm (fits Flashforge AD5X)
- Speaker cavity: 45mm diameter x 48mm tall

### Print Recommendations:
- **Base:** Red PLA
- **Lid:** Red PLA, pause at bow layer and switch to yellow for bow accent
- **Alternative:** Print entire lid in yellow for contrast
