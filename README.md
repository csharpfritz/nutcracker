# Nutcracker Holiday Display

A Blazor Server application for Raspberry Pi Zero that controls a holiday nutcracker decoration with a 32×8 WS2812B LED matrix and synchronized music playback. Features real-time LED lightshows, Bluetooth audio, and a web-based control UI.

## Features
- LED matrix animations synchronized to music
- Blazor Server web interface for control
- Raspberry Pi GPIO and native LED library integration
- Bluetooth audio playback
- Easily extensible with new lightshows and patterns

## Quick Start
1. See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for build and deployment instructions.
2. Hardware setup and wiring: [raspberry-pi-gpio-diagram.md](docs/raspberry-pi-gpio-diagram.md)
3. LED pattern file format: [LED-PATTERN-FILE-FORMAT.md](docs/LED-PATTERN-FILE-FORMAT.md)
4. Lightshow design agent instructions: [LIGHTSHOW_AGENT_INSTRUCTIONS.md](docs/LIGHTSHOW_AGENT_INSTRUCTIONS.md)
5. Hardware shopping: [hardware-shopping-list.md](docs/hardware-shopping-list.md)

## Documentation
- [Session Notes](docs/SESSION-NOTES.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Raspberry Pi GPIO Diagram](docs/raspberry-pi-gpio-diagram.md)
- [LED Pattern File Format](docs/LED-PATTERN-FILE-FORMAT.md)
- [Lightshow Agent Instructions](docs/LIGHTSHOW_AGENT_INSTRUCTIONS.md)
- [LED Native Library](docs/LED-NATIVE-LIBRARY.md)
- [Enclosure Design Notes](docs/ENCLOSURE-DESIGN-NOTES.md)
- [Printer Sizing Notes](docs/PRINTER-SIZING-NOTES.md)
- [Hardware Shopping List](docs/hardware-shopping-list.md)

## 3D Print Schematics
All enclosure and display 3D models are in the [`schematics/`](schematics/) folder.

## Scripts
All music analysis and lightshow generation scripts are in the [`scripts/`](scripts/) folder.

## Contributing
See the docs above for architecture, hardware, and development workflow details. PRs and new lightshow patterns welcome!

---
Merry Christmas! 🎄
