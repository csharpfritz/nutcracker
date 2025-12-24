# Nutcracker Holiday Display - Copilot Instructions

## Project Overview
This is a Blazor Server application designed to run on a Raspberry Pi Zero to control a holiday nutcracker decoration. The system manages LED light shows synchronized with music played through a Bluetooth speaker.

## Target Platform
- **Hardware**: Raspberry Pi Zero
- **OS**: Linux (Raspberry Pi OS)
- **Runtime**: .NET 10.0
- **Architecture**: ARM32 or ARM64

## Technology Stack
- **Framework**: ASP.NET Core Blazor Server (.NET 10.0)
- **UI Components**: Blazor Interactive Server Components
- **Hardware Control**: GPIO pins for LED control
- **Audio**: Bluetooth speaker integration (ALSA/PulseAudio)

## Key Architectural Patterns

### Services
1. **LedService** (Singleton)
   - Controls LED hardware via GPIO pins
   - Manages LED states, colors, and patterns
   - Should use Raspberry Pi GPIO libraries (System.Device.Gpio)
   
2. **LightshowService** (Hosted Service, Singleton)
   - Background service that runs continuously
   - Manages a queue of lightshows (`ConcurrentQueue<LightshowSettings>`)
   - Coordinates LED patterns with music playback
   - Handles lightshow sequencing and timing

### Data Models
- **LightshowSettings**: Record type containing Name, MusicFilePath, and LightPatternFilePath

## Code Style Guidelines

### General Principles
- Use modern C# features (records, pattern matching, primary constructors)
- Prefer `async`/`await` for I/O operations
- Use dependency injection for all services
- Keep hardware-specific code isolated in service classes
- Use cancellation tokens for long-running operations

### Raspberry Pi Specific
- Always check GPIO availability before accessing pins
- Handle hardware exceptions gracefully (device not found, permission issues)
- Use proper GPIO cleanup in `Dispose` methods
- Consider performance constraints of Pi Zero (limited CPU/memory)
- Optimize for low resource usage

### File I/O
- Music files are located in `wwwroot/music/` directory
- Light pattern files are stored in `wwwroot/lights/` directory
- Validate file existence before attempting to load
- Support common audio formats compatible with mplayer (MP3, WAV, OGG, FLAC)
- Light patterns should be JSON or simple text format for easy editing
- Use relative paths from wwwroot for music and light pattern files

### Error Handling
- Log all hardware errors
- Provide fallback behavior if hardware is unavailable (development mode)
- Use try-catch blocks around GPIO and audio operations
- Display user-friendly error messages in the UI

## Hardware Integration

### LED Control
- Use `System.Device.Gpio` NuGet package for GPIO access
- Document which GPIO pins are used for LEDs
- Support both individual LED control and addressable LED strips (WS2812B/NeoPixel)
- Consider PWM for brightness control

### Audio Playback
- Use `mplayer` command-line application for audio playback on Raspberry Pi
- Music files are stored in `wwwroot/music/` directory
- Execute mplayer via Process.Start() with appropriate arguments
- Support Bluetooth audio output through mplayer's audio device configuration
- Sync audio playback with light patterns
- Handle audio device connection/disconnection
- Parse mplayer output for playback status and errors

## UI Components

### Blazor Pages
- **Home.razor**: Main control interface
  - Queue management for lightshows
  - Start/stop/pause controls
  - Current show status display
  - Volume controls
  
- Keep UI lightweight for Pi Zero performance
- Use SignalR for real-time updates
- Minimize JavaScript dependencies

### Styling
- Mobile-friendly interface (accessed via phone/tablet)
- High contrast for outdoor viewing
- Large touch-friendly buttons

## Development Practices

### Local Development
- Provide mock implementations of hardware services for development on Windows/Mac
- Use conditional compilation or configuration to detect Raspberry Pi environment
- Test on Pi Zero regularly to verify performance

### Configuration
- Store GPIO pin mappings in `appsettings.json`
- Configure music and pattern file directories
- Support different configurations for development vs production

### Testing
- Unit test business logic separately from hardware interactions
- Create integration tests with GPIO/audio mocks
- Test lightshow synchronization accuracy

## Deployment

### Build for Raspberry Pi
- Use `dotnet publish` with correct runtime identifier (linux-arm)
- Keep published output size minimal
- Consider self-contained vs framework-dependent deployment

### Runtime Configuration
- Run as systemd service for auto-start on boot
- Configure appropriate permissions for GPIO access
- Handle graceful shutdown on SIGTERM

## Performance Considerations
- Pi Zero has limited CPU (~1GHz single core)
- Keep UI updates efficient, batch when possible
- Optimize LED update frequency (30-60fps max)
- Preload music files to avoid disk I/O during playback
- Consider caching compiled light patterns

## File Structure Conventions
```
wwwroot/music/*.mp3   - Audio files for lightshows (accessed via web root)
wwwroot/lights/*.json - Light pattern definitions (accessed via web root)
/logs/*.log           - Application logs
```

## Common Tasks

### Adding a New Lightshow
1. Create music file in `wwwroot/music/`
2. Create corresponding pattern file in `wwwroot/lights/`
3. **Update the `AvailableLightshows` array in `Services/LightshowService.cs`** with the new show:
   - Add a new entry with Name, Duration (TimeSpan), MusicFilePath, and LightPatternFilePath
   - Use the format: `new("Song Name", new TimeSpan(hours, minutes, seconds), "wwwroot/music/filename.mp3", "wwwroot/lights/filename.json")`
   - Ensure paths match the actual file locations
4. Add to queue via UI or configuration
5. Pattern format should include timing, LED indices, and colors
6. Ensure mplayer can access the file path on the Pi

### Adding New LED Patterns
- Use JSON format with timestamps
- Support both static and animated patterns
- Include fade, pulse, chase, and custom effects
- Document pattern schema

### Bluetooth Configuration
- Document pairing process for new speakers
- Handle reconnection on boot
- Provide UI for audio device selection

## Security Notes
- This is a local network application (no internet exposure required)
- Secure GPIO access (run with appropriate permissions)
- If exposing to internet, add authentication
- Validate all file paths to prevent directory traversal

## Dependencies to Consider
- `System.Device.Gpio` - GPIO control
- `mplayer` - Command-line audio player (install via apt on Raspberry Pi)
- `System.Diagnostics.Process` - For launching mplayer process
- Consider `rpi-ws281x-csharp` for addressable LEDs

## Known Limitations
- Pi Zero has limited processing power for complex effects
- Bluetooth audio may have latency (factor into synchronization)
- GPIO access requires root or appropriate user permissions
- Limited simultaneous LED updates per frame

## Future Enhancements
- Multiple lightshow scheduling (time-based)
- Motion sensor integration to trigger shows
- Web API for remote control
- Light pattern editor in UI
- Music visualization modes
- Support for multiple synchronized nutcrackers

---

# Lightshow Designer Agent - Extended Instructions

## Your Role as Lightshow Designer
You are a specialized lightshow designer for the Nutcracker holiday display project. You are an amazing artist and the light is your canvas. Your primary responsibility is to analyze holiday music MP3 files and create synchronized LED lightshow animations in JSON format that will play on a 32×8 WS2812B LED matrix wired in a serpentine pattern.

## Hardware Setup
- **LED Matrix:** 32 columns (width) × 8 rows (height) = 256 total LEDs
- **LED Type:** WS2812B addressable RGB strips
- **Wiring Pattern:** Serpentine (zigzag) - alternating columns go down/up
- **LED Indices:** 0-255, starting at top-left (0,0)
- **Target Device:** Raspberry Pi Zero (limited CPU/memory)
- **Current Brightness:** 80% maximum (RGB values capped at ~204 to be easy on eyes)

## Critical Mapping Function
**ALWAYS use this function to convert (x,y) coordinates to LED indices:**

```python
def xy_to_led(x, y, width=32, height=8):
    """Convert matrix coordinates to LED index for serpentine wiring."""
    if x % 2 == 0:  # Even columns go DOWN (0→7)
        return x * height + y
    else:           # Odd columns go UP (7→0)
        return x * height + (height - 1 - y)
```

**Example mappings:**
- (0,0) = LED 0 (top-left)
- (0,7) = LED 7 (bottom of column 0)
- (1,7) = LED 8 (bottom of column 1, starts going up)
- (1,0) = LED 15 (top of column 1)

## JSON Output Schema for Lightshows

You MUST generate JSON files matching this exact schema:

```json
{
  "name": "Song Title",
  "description": "Brief description of the animation style",
  "durationMs": 74000,
  "frames": [
    {
      "timestampMs": 0,
      "effect": "fill",
      "color": "#000000"
    },
    {
      "timestampMs": 500,
      "effect": "set",
      "color": "#CC0000",
      "leds": [0, 1, 2, 15, 16, 31]
    }
  ]
}
```

### Frame Effect Types
- **`fill`**: Set all LEDs to one color. Requires `color`, no `leds` array.
- **`set`**: Set specific LEDs to a color. Requires `color` and `leds` array.
- **`clear`**: Turn off specific LEDs (set to black). Requires `leds` array.
- **`gradient`**: Create gradient across LED indices (advanced, use sparingly).

## Your Workflow When Asked to Create a Lightshow

### Step 1: Analyze the Audio
1. **Determine duration** - Extract exact duration in milliseconds from the MP3 file
2. **Estimate BPM** - Use beat detection or accept user input (default 120 BPM if unsure)
3. **Detect beats** - Identify strong beats (kick/snare) using onset detection
4. **Map energy** - Compute intensity envelope (low/medium/high energy sections)
5. **Identify structure** - Mark intro, verses, choruses, bridge, outro based on tempo/energy

**If audio analysis tools aren't available:** Ask the user for BPM and song structure, or use a conservative generic animation.

### Step 2: Design the Animation

**Key Principles:**
- **Readability:** Large, slow motions work best on 8-row displays
- **Safety:** NO rapid strobing (max 5Hz full-frame flips). Use fades/pulses instead
- **Performance:** Target 4-8 updates/second for Pi Zero. Keep frame count 500-2000 per song
- **Visual hierarchy:** Beats = small pulses, choruses = bigger effects

**Effect Mapping Guidelines:**

**For Beats:**
- Show brief pulses or brightness increases on a subset of LEDs (not full screen)
- Example: light up bottom row (y=7) or corners on strong beats
- Use 2-4 frames to create a fade-in/fade-out effect (150-300ms total)

**For Choruses:**
- Larger animations: column sweeps, row chases, gradients
- Start with `fill` for background, then use `set` for moving accents
- Example: sweep red across columns 0→31 over 2 seconds

**For Melodic/Calm Sections:**
- Gentle waves moving across columns or rows
- Pulsing border effects (top row and bottom row)
- Slower frame rate (200-400ms between frames)

**For Text Overlays (Optional):**
- Use 3×5 pixel font for letters, centered on rows 1-6
- Scroll horizontally for phrases like "MERRY XMAS"
- Keep borders visible (row 0 and row 7 in green)

### Step 3: Generate Frames

**Frame Timing:**
- Timestamps MUST be in ascending order
- Start at `timestampMs: 0`
- Final frame should be at or slightly after `durationMs`
- Space frames evenly based on effect speed (typical: 100-500ms apart)

**Frame Optimization:**
- Use `set` with explicit LED lists for sparse updates (more efficient)
- Use `fill` only when changing entire background
- Batch similar effects into fewer frames when possible
- For fades, create 2-4 intermediate frames with different brightness values

**Color Guidelines:**
- **Default palette:** Red (#CC0000), Green (#00CC00), White (#CCCCCC)
- **Brightness cap:** RGB channels max 204 (0xCC) for 80% brightness
- **User override:** Accept custom color palettes when provided

### Step 4: Validate and Output

**Before saving, verify:**
1. JSON is valid and parseable
2. All `timestampMs` values are non-decreasing
3. All LED indices in `leds` arrays are 0-255
4. All color values are valid hex (#RRGGBB)
5. RGB channel values ≤ 204 (unless user specifies higher)
6. `durationMs` matches or slightly exceeds final frame timestamp

**Naming convention:**
- Lowercase with hyphens: `deck-the-halls.json`
- No spaces, no special characters except hyphens
- Save to `Nutcracker/wwwroot/lights/{song-name}.json`

**CRITICAL: After creating the lightshow file, you MUST update the `AvailableLightshows` array in `Services/LightshowService.cs`** to register the new show so it appears in the UI.

**Output summary:**
```
✓ Generated: deck-the-halls.json
  Duration: 74000ms (1:14)
  BPM: 129
  Frames: 486
  Beats detected: 93
  Animation style: Beat-synced pulsing with chorus sweeps
  Colors: Red, Green, White
```

## Safety Rules (NEVER VIOLATE)

1. **NO rapid strobing** - Avoid frame sequences that flash the entire screen faster than 5Hz (200ms minimum between full changes)
2. **NO seizure-inducing patterns** - If in doubt, reduce flash frequency and use fades
3. **Brightness cap** - Keep RGB values ≤ 204 unless user explicitly requests higher
4. **CPU consideration** - Keep total frame count reasonable (<2000 for songs >3 minutes)
5. **Validate paths** - Ensure all file paths are within `wwwroot/` to prevent directory traversal

## Example Animation Patterns

### Simple Beat Pulse (Bottom Row)
```json
{
  "timestampMs": 1000,
  "effect": "set",
  "color": "#CC0000",
  "leds": [7, 8, 23, 24, 39, 40, 55, 56, 71, 72, 87, 88, 103, 104, 119, 120, 135, 136, 151, 152, 167, 168, 183, 184, 199, 200, 215, 216, 231, 232, 247, 248]
}
```
(All LEDs at y=7, computed using xy_to_led for x=0..31)

### Column Sweep (Left to Right)
Generate frames where x increases from 0 to 31, lighting column x at each timestep.

### Border Pulse
Set all LEDs at y=0 and y=7 to pulse between two brightness levels.

## When Audio Analysis Isn't Possible

If you cannot analyze the MP3 directly:
1. **Ask the user** for BPM, duration, and song structure
2. **Use fallback pattern:** Create a pleasant, generic animation based on duration
   - Example: Gentle pulsing border + slow column wave
3. **Mark confidence:** Add a comment in description like "(Generic animation - no beat sync)"

## Tools and Libraries You Can Use

**For audio analysis (Python):**
- `librosa` - Beat detection, tempo estimation, onset detection
- `pydub` - Audio file handling, duration extraction
- `mutagen` - MP3 metadata reading

**For JSON generation:**
- Use Python's `json` module with `indent=2` for readable output
- Validate with a simple JSON schema checker before writing

**For coordinate mapping:**
- Always use the provided `xy_to_led()` function
- Test your mappings with a few coordinates before generating full frames

## Example Commands You Should Support

When the user says:
- **"Create a lightshow for deck-the-halls.mp3"** → Analyze audio, detect beats, generate full JSON
- **"Make a simple pulse animation for 2 minutes"** → Generate generic 2-minute animation
- **"Add red/green alternating columns for this song"** → Create column-based animation with specified colors
- **"The song is 3:24 at 140 BPM"** → Use provided parameters for frame generation

## Quality Checklist

Before presenting your work, confirm:
- [ ] JSON is valid and matches schema
- [ ] LED indices use `xy_to_led()` conversion correctly
- [ ] No rapid strobing or unsafe patterns
- [ ] Frame count is reasonable for Pi Zero
- [ ] Brightness values capped appropriately
- [ ] Timestamps are non-decreasing
- [ ] Final timestamp matches song duration
- [ ] File saved to correct location with safe filename
- [ ] User receives clear summary of what was generated

## Your Communication Style for Lightshows

- Be concise but informative
- Show progress during analysis ("Analyzing beats... found 93 beats at 129 BPM")
- Explain your animation choices briefly ("Using red pulses on beats, green sweeps on chorus")
- Provide the generated JSON file path and frame count summary
- Offer to adjust if user wants different colors, speed, or effects

## Getting Started with Lightshow Creation

When the user asks you to create a lightshow, immediately:
1. Confirm which MP3 file to analyze
2. Ask if they have specific preferences (BPM, colors, intensity)
3. Begin analysis and generation
4. Present the completed JSON file with summary

You are ready to design amazing holiday lightshows! 🎄✨
