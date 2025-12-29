# LED Control with Native rpi_ws281x Library

This project uses P/Invoke to call the native `rpi_ws281x` library directly from C#, providing full control over WS2812B LED strips with precise timing.

## Why Native Library?

The Python test script (`led_matrix_test.py`) works because it uses the `rpi_ws281x` library (via Adafruit NeoPixel), which provides hardware-accurate PWM timing for WS2812B LEDs. The previous C# approach using SPI didn't work reliably because:

1. **WS2812B requires precise PWM timing** (350ns/700ns pulses)
2. **SPI protocol doesn't match WS2812B timing** requirements
3. **The native library uses DMA + PWM** for accurate signal generation

## Architecture

```
C# Application (LedService.cs)
    ↓ P/Invoke
Ws2811Native.cs (P/Invoke wrapper)
    ↓ Native calls
libws2811.so (Native C library)
    ↓ Hardware control
GPIO 18 (PWM0) → WS2812B LED Strip
```

## Installation on Raspberry Pi

### 1. Install the Native Library

Run the installation script:
```bash
chmod +x install_native_led_library.sh
./install_native_led_library.sh
```

This will:
- Clone and build the `rpi_ws281x` library
- Install `libws2811.so` to `/usr/local/lib/`
- Set up proper library paths

### 2. Grant Permissions

The application needs DMA and hardware access. Either:

**Option A: Run with sudo** (simplest)
```bash
sudo ./Nutcracker
```

**Option B: Set capabilities** (more secure)
```bash
sudo setcap 'cap_dma=ep cap_sys_admin=ep' ./Nutcracker
./Nutcracker
```

## Hardware Connection

```
Raspberry Pi         WS2812B LED Strip
----------------------------------------
GPIO 18 (Pin 12) --> DIN (Data Input)
5V Power         --> VCC (or use external 5V supply)
Ground           --> GND
```

**Important Notes:**
- GPIO 18 is the PWM0 pin (Physical Pin 12)
- For many LEDs, use an external 5V power supply
- Add a 300-470 ohm resistor between GPIO 18 and DIN
- Add a 1000µF capacitor across power supply

## Configuration

Edit `LedService.cs` constants if needed:

```csharp
private const int GPIO_PIN = 18;        // GPIO pin
private const int DMA_CHANNEL = 10;     // DMA channel (10 is safe)
private const uint TARGET_FREQ = 800000; // 800kHz for WS2812B
private const byte DEFAULT_BRIGHTNESS = 255; // 0-255
```

### LED Strip Color Order

Most WS2812B use GRB order, but if colors are wrong:
```csharp
strip_type = (int)WS2811_STRIP_GRB  // Default (Green, Red, Blue)
// Or try:
strip_type = (int)WS2811_STRIP_RGB  // Red, Green, Blue
strip_type = (int)WS2811_STRIP_BGR  // Blue, Green, Red
```

## Development

The service automatically detects if running on Raspberry Pi:
- **Linux ARM**: Uses native library
- **Other platforms**: Uses mock mode (logs only)

## Library Reference

- **Source**: https://github.com/jgarff/rpi_ws281x
- **Documentation**: See `ws2811.h` in the repository
- **Library location**: `/usr/local/lib/libws2811.so`

## Troubleshooting

### "Failed to initialize LED strip"
1. Make sure library is installed: `ls -l /usr/local/lib/libws2811.so`
2. Run with sudo: `sudo ./Nutcracker`
3. Check GPIO is not in use: `sudo fuser /dev/gpiomem`

### Colors are wrong
Change the `strip_type` in `LedService.cs` initialization

### LEDs flicker or show wrong colors
- Check power supply (insufficient power is common)
- Verify wiring and connections
- Reduce brightness in code

### DllNotFoundException
The library isn't installed. Run `install_native_led_library.sh`

## Performance

The native library provides:
- **Precise timing**: Hardware PWM + DMA
- **High frame rates**: 60+ FPS easily achievable
- **Low CPU usage**: DMA handles data transfer
- **Reliable operation**: Same code Python uses

## Comparison with Python

| Aspect | Python (rpi_ws281x) | C# (P/Invoke) |
|--------|---------------------|---------------|
| Library | Python wrapper | Direct P/Invoke |
| Performance | Good | Excellent |
| Control | High-level API | Full control |
| Integration | External process | Native |
| Timing | Library-controlled | Library-controlled |

Both use the same underlying native library, so reliability is identical!
