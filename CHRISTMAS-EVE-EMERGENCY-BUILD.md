# Nutcracker Holiday Display - Christmas Eve Emergency Build

**Date:** December 24, 2025, 5:40 PM
**Deadline:** Christmas Morning (8 AM)
**Available Time:** ~14 hours

---

## EMERGENCY PARTS GENERATED ✅

Two STL files created for minimal working setup:

### 1. **emergency-led-plaque.stl** (120 KB)
- **Location:** `D:\Nutcracker\Nutcracker\wwwroot\emergency-led-plaque.stl`
- **Description:** Flat LED plaque (32cm x 8cm), split into 2 halves
- **Features:**
  - Built-in clips to hold LED matrix (no glue needed)
  - Alignment pins to join left and right halves
  - 4 mounting holes at corners (M4 screws)
  - Wire pass-through hole at bottom center
- **Print Time:** 3-4 hours
- **Print Settings:**
  - Material: Red PLA
  - Layer Height: 0.2mm
  - Infill: 15-20%
  - Supports: Minimal (for clips)
  - Adhesion: Brim

### 2. **emergency-platform-base.stl** (106 KB)
- **Location:** `D:\Nutcracker\Nutcracker\wwwroot\emergency-platform-base.stl`
- **Description:** 200mm square platform base
- **Features:**
  - 4 nutcracker mounting holes (50mm x 60mm spacing, M4 screws)
  - 4 corner holes to bolt platform to table/board
  - Simple flat design, no enclosure
- **Print Time:** 2-3 hours
- **Print Settings:**
  - Material: Red PLA
  - Layer Height: 0.2mm
  - Infill: 20%
  - Supports: None needed
  - Adhesion: Brim

---

## TONIGHT'S PRINT SCHEDULE

**Current Status:**
- ✅ Gift box printing (should be done by ~6 PM)

**Next Steps:**

| Time | Action | Duration |
|------|--------|----------|
| 6:00 PM | Start LED plaque | 3-4 hours |
| 9:30 PM | Start platform base | 2-3 hours |
| 12:30 AM | **DONE!** All parts printed | - |

**Total Print Time:** 5-7 hours

---

## ASSEMBLY (Christmas Morning)

### Hardware Needed:
- **8x M4 screws** (various lengths)
  - 4x M4 x 12mm - Nutcracker to platform
  - 4x M4 x 8mm - LED plaque to nutcracker (optional)

### Assembly Steps:

1. **Join LED Plaque Halves**
   - Align the two halves
   - Press alignment pins into holes
   - They snap together

2. **Install LED Matrix**
   - Place LED strip onto plaque backing
   - Connectors face backward (out the wire hole)
   - Press edges under the clips
   - LEDs held securely without glue

3. **Mount Nutcracker to Platform**
   - Place nutcracker on platform (centered)
   - Align with 4 mounting holes (50x60mm pattern)
   - Insert M4 screws through platform into nutcracker base
   - Tighten securely

4. **Attach LED Plaque** (Optional)
   - Use 4 corner mounting holes on plaque
   - Screw directly to nutcracker or use standoffs
   - Or prop it against nutcracker

5. **Electronics Setup** (Temporary)
   - Pi and battery can sit loose in/under platform
   - Or place in gift box nearby
   - Connect LED matrix to Pi GPIO
   - Connect power

---

## WHAT'S NOT INCLUDED (Print After Christmas)

This is a minimal emergency build. After Christmas, you can print:

### Full Enclosure System:
1. **Box Base** (6-8 hours)
   - Enclosed cavity for Pi + battery
   - Pi mounting standoffs
   - Port access cutouts
   - Ventilation

2. **Lid** (2-3 hours)
   - Battery access cutout
   - Screw-on design

3. **Curved LED Display** (8-12 hours total)
   - Left half (4-6 hours)
   - Right half (4-6 hours)
   - Curved backing for more dramatic look
   - Mounts to front of box base

**Files:** Already designed in `nutcracker-enclosure.scad`

---

## FILE LOCATIONS

### Emergency Files (Tonight):
```
D:\Nutcracker\Nutcracker\wwwroot\
  ├── emergency-led-plaque.stl
  ├── emergency-platform-base.stl
  ├── emergency-led-plaque.scad (source)
  └── emergency-platform-base.scad (source)
```

### Gift Box (Done):
```
D:\Nutcracker\Nutcracker\wwwroot\
  └── speaker-gift-box-complete.stl
```

### Full Enclosure (For Later):
```
D:\Nutcracker\Nutcracker\wwwroot\
  ├── nutcracker-enclosure.scad (source)
  ├── nutcracker-box-base.stl
  └── (lid and display parts need to be generated)
```

---

## TROUBLESHOOTING

### LED Plaque Issues:
- **Halves won't join:** File down alignment pins slightly
- **LEDs don't fit:** Clips may be too tight - carefully bend them back
- **LEDs fall out:** Add a tiny drop of hot glue at corners (removable)

### Platform Issues:
- **Nutcracker holes don't align:** Check you're using 50x60mm spacing
- **Platform warps:** Print with brim, ensure bed is level

### Electronics:
- **LEDs don't light:** Check GPIO pin connections (GPIO 18 for data)
- **Pi won't boot:** Check power supply (5V 3A minimum)
- **App won't run:** Check logs: `sudo journalctl -u nutcracker -n 50`

---

## HARDWARE SHOPPING LIST

Located in: `D:\Nutcracker\hardware-shopping-list.md`

**Emergency Hardware Needed Tonight:**
- 8x M4 screws (assorted 8-12mm lengths)
- Small screwdriver

**Full Hardware List:**
- M4 screws (nutcracker mounting)
- M3 screws (display mounting)
- M2.5 screws (Pi mounting)
- #6 sheet metal screws (lid)

---

## SOFTWARE/LIGHTSHOW FILES

### Music Files:
```
D:\Nutcracker\Nutcracker\wwwroot\music\
  ├── bruce-springsteen.mp3
  └── (other songs)
```

### Light Pattern Files:
```
D:\Nutcracker\Nutcracker\wwwroot\lights\
  ├── bruce-springsteen.json
  └── (other patterns)
```

### Python Scripts:
```
D:\Nutcracker\
  ├── analyze_pattern.py
  ├── create_wizards_lightshow_v2.py
  └── (other analysis tools)
```

---

## NEXT STEPS AFTER CHRISTMAS

1. **Print Full Enclosure Parts**
   - Generate individual STLs from `nutcracker-enclosure.scad`
   - Box base, lid, curved display halves
   - Total ~18-23 hours printing

2. **Create More Lightshows**
   - Use lightshow designer agent instructions
   - Analyze MP3 files with `librosa`
   - Generate JSON patterns with beat sync

3. **Hardware Assembly**
   - Mount Pi 3B properly inside enclosure
   - Wire battery pack cleanly
   - Install curved LED display

4. **Software Updates**
   - Add more songs to `AvailableLightshows` array
   - Test lightshow timing
   - Configure Bluetooth speaker pairing

---

## IMPORTANT NOTES

✅ **What Works for Christmas:**
- LED plaque with clips (holds matrix securely)
- Platform base (mounts nutcracker)
- Gift box (holds speaker)
- All parts tested and should work

⚠️ **Temporary Compromises:**
- Pi/battery loose (not enclosed)
- Flat plaque (not curved)
- Manual wiring (not organized in box)

🎄 **This Gets You a Working Display for Christmas Morning!**

Print the full enclosure system after the holidays at your leisure.

---

## CONTACT/RESUME

All design files, STLs, and source code are in:
```
D:\Nutcracker\
```

Key files to resume work:
- `nutcracker-enclosure.scad` - Full enclosure design
- `speaker-gift-box.scad` - Gift box design
- `emergency-led-plaque.scad` - Tonight's LED plaque
- `emergency-platform-base.scad` - Tonight's platform
- `SESSION-NOTES.md` - Development notes
- `hardware-shopping-list.md` - Complete hardware list

**Merry Christmas! 🎄🎅✨**

---

*Generated: December 24, 2025, 5:40 PM*
*Deadline: Christmas Morning, 8:00 AM*
*Status: Emergency minimal build in progress*
