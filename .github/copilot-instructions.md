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
3. Add to queue via UI or configuration
4. Pattern format should include timing, LED indices, and colors
5. Ensure mplayer can access the file path on the Pi

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
