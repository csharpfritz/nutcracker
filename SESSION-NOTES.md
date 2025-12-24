# Nutcracker LED Display - Session Notes
**Last Updated:** December 23, 2024 11:41 PM EST

## Project Overview
Blazor Server application running on Raspberry Pi Zero controlling a holiday nutcracker decoration with LED matrix and Bluetooth audio.

## Hardware Configuration

### Raspberry Pi Details
- **Hostname:** `nutcracker-2`
- **SSH Access:** `jfritz@nutcracker-2`
- **User:** jfritz
- **Deployment Path:** `/home/jfritz/www/`
- **Service:** `nutcracker.service` (systemd service, runs with sudo)

### LED Matrix Configuration
- **Type:** WS2812B addressable RGB LED strip
- **Total LEDs:** 256 (8 rows × 32 columns)
- **GPIO Pin:** 10 (SPI0 MOSI - Physical Pin 19)
- **DMA Channel:** 10
- **Frequency:** 800kHz
- **Current Brightness:** 80% (204/255) - reduced from 100% to be easier on eyes

### LED Matrix Wiring Pattern
- **Layout:** 8 rows tall × 32 columns wide
- **Wiring:** Serpentine/zigzag pattern
- **LED 0 Position:** Top-left corner
- **Pattern:**
  - Column 0 (LEDs 0-7): Goes DOWN from top to bottom
  - Column 1 (LEDs 8-15): Goes UP from bottom to top (serpentine)
  - Column 2 (LEDs 16-23): Goes DOWN again
  - Pattern continues alternating
- **Coordinate Conversion Function:**
  ```python
  def xy_to_led(x, y, width=32, height=8):
      if x % 2 == 0:  # Even columns go down
          return x * 8 + y
      else:  # Odd columns go up
          return x * 8 + (7 - y)
  ```

### Audio Configuration
- **Output:** Bluetooth speaker
- **Device:** B19 Pro (MAC: 46:5A:8F:27:9F:4D)
- **Status:** Connected and paired
- **Default Sink:** `bluez_output.46_5A_8F_27_9F_4D.1` (PulseAudio/PipeWire)
- **System Volume:** 73% (controlled via amixer)
- **Player:** mplayer (requires TERM=dumb and PULSE_SERVER environment variables to work in systemd service)

## Application Structure

### Key Files
- **Main Service:** `Nutcracker/Services/LightshowService.cs` - Manages queue and playback
- **LED Control:** `Nutcracker/Services/LedService.cs` - Controls LED hardware
- **Native Library:** `Nutcracker/Services/Ws2811Native.cs` - P/Invoke to libws2811.so
- **UI:** `Nutcracker/Components/Pages/Home.razor` - Web interface
- **Music Files:** `wwwroot/music/*.mp3`
- **Light Patterns:** `wwwroot/lights/*.json`

### Deployment Process
1. Stop service: `ssh jfritz@nutcracker-2 "sudo systemctl stop nutcracker"`
2. Build on Windows: `dotnet publish -c Release` (from D:\Nutcracker)
3. Files auto-deploy to Pi (configured in project)
4. Start service: `ssh jfritz@nutcracker-2 "sudo systemctl start nutcracker"`

### Service Management
- **View logs:** `ssh jfritz@nutcracker-2 "sudo journalctl -u nutcracker --no-pager -n 50"`
- **Status:** `ssh jfritz@nutcracker-2 "sudo systemctl status nutcracker --no-pager"`
- **Stop:** `ssh jfritz@nutcracker-2 "sudo systemctl stop nutcracker"`
- **Start:** `ssh jfritz@nutcracker-2 "sudo systemctl start nutcracker"`
- **Restart:** `ssh jfritz@nutcracker-2 "sudo systemctl restart nutcracker"`

## Current LED Patterns

### Idle Display: "MERRY" Text
**File:** `wwwroot/lights/merry-christmas-static.json`

**Design:**
- Red text "MERRY" centered vertically (rows 1-6)
- Green border lines at top (row 0) and bottom (row 7)
- Black background everywhere else
- Font: 3x5 pixel letters with 1-column spacing between letters
- Static display (holds for 5 minutes before looping)

### Enhancement: Full "MERRY CHRISTMAS" Scrolling Idle Display
**Goal:** Extend the idle display so it shows the full phrase "MERRY CHRISTMAS" scrolling right-to-left across the matrix, rather than only "MERRY". The scroll should be smooth, readable, and repeat indefinitely.

**Why:** The full phrase is more festive for viewers and leverages the existing 32×8 matrix by scrolling text across rather than fitting a shorter centered word.

**Acceptance Criteria:**
- The full text "MERRY CHRISTMAS" scrolls from right-to-left and repeats infinitely.
- Text is red, vertically centered on rows 1-6, with 1-column spacing between letters using the 3x5 font.
- Top and bottom green borders remain visible during scrolling.
- Default scroll speed is readable (approx. 120ms/column) and configurable via the JSON pattern.
- LightshowService falls back to `merry-christmas-static.json` if the scrolling file is missing.

**Implementation Steps:**
1. Verify `wwwroot/lights/merry-christmas-scrolling.json` contains a `scrollMs` parameter and frames representing a full cycle (text width + display width).
2. If not present, generate the JSON: render the text into a bitmap (width = text pixel width), produce frames shifting the bitmap left by one column per `scrollMs`, and add border frames for top/bottom green rows.
3. Ensure frames use `set` and `clear` effects with exact LED indices computed via `xy_to_led(x, y)` to match serpentine wiring.
4. Update `LightshowService.cs` (optional) to use `merry-christmas-scrolling.json` as the idle pattern when queue is empty.
5. Deploy and test on Pi using the web UI "Test LEDs" and by running the service.

**Quick Test Commands:**
```bash
# On the Pi - test pattern file exists
ls -la /home/jfritz/www/wwwroot/lights/merry-christmas-scrolling.json

# Trigger a test from the web UI or restart the service after deploy
sudo systemctl restart nutcracker
sudo journalctl -u nutcracker --no-pager -n 100
```

**Notes:** If the Pi Zero struggles with rendering many frames at `120ms` per column, increase `scrollMs` to reduce CPU load or precompute fewer frames and loop them.

**LED Mappings:**
- **Red LEDs (MERRY):** [9, 10, 11, 12, 13, 14, 18, 25, 26, 27, 28, 29, 30, 41, 42, 43, 44, 45, 46, 49, 51, 54, 57, 62, 73, 74, 75, 76, 77, 78, 81, 83, 89, 90, 91, 93, 94, 105, 106, 107, 108, 109, 110, 113, 115, 121, 122, 123, 125, 126, 140, 141, 142, 148, 149, 150, 156, 157, 158]
- **Green LEDs (borders):** [0, 7, 8, 15, 16, 23, 24, 31, 32, 39, 40, 47, 48, 55, 56, 63, 64, 71, 72, 79, 80, 87, 88, 95, 96, 103, 104, 111, 112, 119, 120, 127, 128, 135, 136, 143, 144, 151, 152, 159, 160, 167, 168, 175, 176, 183, 184, 191, 192, 199, 200, 207, 208, 215, 216, 223, 224, 231, 232, 239, 240, 247, 248, 255]

### Light Pattern JSON Format
```json
{
  "name": "Pattern Name",
  "description": "Description",
  "durationMs": 300000,
  "frames": [
    {
      "timestampMs": 0,
      "effect": "fill|set|clear|gradient",
      "color": "#RRGGBB",
      "leds": [array of LED indices]
    }
  ]
}
```

## Issues Fixed This Session

### 1. LED Matrix Wiring Discovery
**Problem:** Text displaying as scattered LEDs, unreadable  
**Solution:** Tested matrix with Python scripts to determine serpentine wiring pattern, created xy_to_led() conversion function  
**Testing Script Location:** `/tmp/test_merry5.py` on Pi (various test scripts created)

### 2. LED Brightness Too High
**Problem:** LEDs hurt eyes at full brightness  
**Solution:** Changed `DEFAULT_BRIGHTNESS` from 255 to 204 (80%) in LedService.cs line 24

### 3. Music Not Playing Through Bluetooth
**Problem:** mplayer process exiting immediately when run as systemd service  
**Root Cause:** Missing TERM environment variable and PulseAudio server path  
**Solution:** Added to LightshowService.cs ProcessStartInfo:
```csharp
Environment = 
{
    ["TERM"] = "dumb",
    ["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"
}
```

### 4. Skip Button Not Working
**Problem:** Skip button in UI not stopping music playback  
**Root Cause 1:** Added `ReadToEndAsync()` on stderr which blocked until process ended  
**Root Cause 2:** Cancellation didn't kill the mplayer process  
**Solution:** 
- Removed blocking stderr read
- Added process.Kill() in OperationCanceledException catch block (LightshowService.cs lines 179-192)

### 5. Pattern Blinking Rapidly
**Problem:** LED pattern looping every 100ms causing seizure-inducing flashing  
**Solution:** Added dummy frame at 299900ms to make pattern static for 5 minutes

## Available Lightshows
Located in `LightshowService.cs` AvailableLightshows array:
1. Santa Claus Is Comin To Town (4:28) - Bruce Springsteen
2. Deck the Halls (1:14)
3. Grandma Got Run Over By A Reindeer (3:24) - Elmo & Patsy
4. Rudolph the Red-Nosed Reindeer (3:08) - Gene Autry
5. Hark the Herald Angels Sing (4:41) - Celtic Christmas
6. Joy to the World (2:03)
7. O Come All Ye Faithful (5:22) - Celtic Christmas
8. Oh Christmas Tree (1:41)
9. Santa Claus Is Coming to Town (Piano) (1:49)
10. Silent Night (2:51)
11. Wizards in Winter (3:05) - Trans-Siberian Orchestra

**Note:** Most songs are missing light pattern JSON files (only merry-christmas-static.json exists currently)

## Testing LED Patterns

### Quick Test Script Template (Python)
```python
#!/usr/bin/env python3
import time, ctypes

lib = ctypes.CDLL('/usr/local/lib/libws2811.so')

# [Structure definitions omitted for brevity - see test_merry5.py]

def xy_to_led(x, y):
    if x < 0 or x >= 32 or y < 0 or y >= 8:
        return None
    if x % 2 == 0:
        return x * 8 + y
    else:
        return x * 8 + (7 - y)

# Create pattern, set pixels, show()
```

**Process:**
1. SSH to Pi: `ssh jfritz@nutcracker-2`
2. Stop service: `sudo systemctl stop nutcracker`
3. Create script: `cat > /tmp/test.py << 'EOF' ... EOF`
4. Run: `sudo python3 /tmp/test.py`
5. Restart service: `sudo systemctl start nutcracker`

## Web Interface
- **URL:** `http://nutcracker-2:3000` or `http://<pi-ip>:3000`
- **Features:**
  - Now Playing display with song name and duration
  - Volume slider (0-100%)
  - LED Brightness slider (0-100%)
  - Skip button (✓ working as of this session)
  - Queue display ("Up Next")
  - Available songs grid with "Add to Queue" buttons
  - Settings section with "Test LEDs" button

## Known Issues / TODO

### Missing Light Patterns
Most songs don't have light pattern JSON files yet. Currently using fallback animation (moving wave, pulsing, row/column scans).

Pattern files needed:
- santa-claus-is-comin-to-town.json
- deck-the-halls.json
- grandma-got-run-over.json
- rudolph.json
- hark-the-herald.json
- joy-to-the-world.json
- o-come-all-ye-faithful.json
- oh-christmas-tree.json
- santa-claus-piano.json
- silent-night.json
- wizards-in-winter.json

### Path Issue in Logs
Logs show: `Pattern file not found: /home/jfritz/www/wwwroot/wwwroot/lights/...`
Notice the double `wwwroot/wwwroot` - may need to fix path resolution in LedService.cs

## Useful Commands Reference

### Testing Audio
```bash
# Test Bluetooth connection
bluetoothctl devices
bluetoothctl info 46:5A:8F:27:9F:4D

# Check audio sinks
pactl list sinks short
pactl get-default-sink

# Check volume
amixer sget Master

# Test mplayer manually
cd /home/jfritz/www
mplayer -volume 70 -ao pulse "wwwroot/music/deck-the-halls-christmas-bells-129141.mp3"
```

### Testing LEDs
```bash
# Quick LED test (light up LED 0 red for 5 seconds)
sudo python3 << 'EOF'
import time, ctypes
lib = ctypes.CDLL('/usr/local/lib/libws2811.so')
# [Full test code in test scripts]
EOF
```

### File Management
```bash
# Check music files
ls -la /home/jfritz/www/wwwroot/music/

# Check light patterns
ls -la /home/jfritz/www/wwwroot/lights/

# Edit pattern file on Pi
nano /home/jfritz/www/wwwroot/lights/merry-christmas-static.json

# Copy pattern from Windows to Pi
scp "D:\Nutcracker\Nutcracker\wwwroot\lights\*.json" jfritz@nutcracker-2:/home/jfritz/www/wwwroot/lights/
```

## Code Architecture Notes

### LightshowService Pattern
- Runs as BackgroundService (ExecuteAsync loop)
- Maintains ConcurrentQueue of lightshows
- When queue empty, plays idle "Merry Christmas" static pattern
- When show queued, stops idle and starts show (music + LED pattern)
- Uses CancellationTokenSource for skip functionality
- Volume control via amixer (system-wide)

### LedService Pattern
- Singleton service
- Uses native libws2811.so via P/Invoke (Ws2811Native.cs)
- Supports matrix operations via row/col coordinates
- Pattern playback via JSON files
- Fallback animations if pattern file missing

### LED Pattern Frame Effects
- **fill:** Set all LEDs to one color
- **set:** Set specific LED indices to a color
- **clear:** Turn off specific LEDs
- **gradient:** Gradient between two colors across LED indices

## Development Workflow
1. Make changes on Windows in Visual Studio / VS Code
2. Stop Pi service via SSH
3. Build: `dotnet publish -c Release` (auto-deploys)
4. Start Pi service via SSH
5. Test via web interface at http://nutcracker-2:3000
6. Check logs if issues: `sudo journalctl -u nutcracker -n 50`

## Success Metrics This Session
✅ LED matrix wiring pattern identified and documented  
✅ "MERRY" text displaying correctly with clean design  
✅ Music playing through Bluetooth speaker  
✅ Skip button fully functional  
✅ Brightness reduced to comfortable level (80%)  
✅ Pattern stable without blinking  
✅ System documented for future sessions  

## Next Steps / Future Work
- [ ] Create light patterns for remaining songs
- [ ] Fix double wwwroot path issue
- [ ] Add more text patterns (XMAS, HAPPY HOLIDAYS, etc.)
- [ ] Consider adding animation patterns (snowflakes, candy canes, etc.)
- [ ] Add schedule/timer functionality for auto-play
- [ ] Motion sensor integration to trigger shows
- [ ] Multiple display patterns/themes

---

## Quick Start for Next Session

1. **Verify system status:**
   ```bash
   ssh jfritz@nutcracker-2 "sudo systemctl status nutcracker"
   ```

2. **Test pattern is still working:**
   - Visit http://nutcracker-2:3000
   - Should see "MERRY" in red with green borders

3. **Test music and skip:**
   - Add song to queue
   - Verify music plays
   - Click skip button to verify it works

4. **Development environment:**
   - Open `D:\Nutcracker` in your IDE
   - Key files: LightshowService.cs, LedService.cs, Home.razor
   - Deploy: `dotnet publish -c Release`
