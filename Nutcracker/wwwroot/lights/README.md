# LED Pattern File Format

LED pattern files define the light animations for the 8x32 LED matrix. Patterns are stored as JSON files in this directory.

## Matrix Layout

- **Dimensions**: 8 rows × 32 columns = 256 LEDs total
- **GPIO Pin**: 18
- **LED Indexing**: 0-255 (0 = top-left, 31 = top-right, 32 = second row left, etc.)
- **LED Type**: WS2812B/NeoPixel addressable LEDs

## Pattern File Structure

```json
{
  "name": "Pattern Name",
  "description": "Brief description of the pattern",
  "durationMs": 10000,
  "frames": [
    // Array of frames with timestamps
  ]
}
```

### Properties

- **name**: Human-readable name for the pattern
- **description**: Optional description of what the pattern does
- **durationMs**: Total duration of the pattern in milliseconds
- **frames**: Array of LED frames to display over time

## Frame Structure

Each frame defines what should happen at a specific timestamp.

```json
{
  "timestampMs": 0,
  "effect": "set",
  "color": "#FF0000",
  "leds": [0, 1, 2, 3]
}
```

### Frame Properties

- **timestampMs**: When to display this frame (milliseconds from start)
- **effect**: Type of effect to apply (see below)
- **color**: Hex color code (e.g., "#FF0000" for red)
- **leds**: Array of LED indices to affect (optional, depends on effect)
- **startColor**: Start color for gradient effects
- **endColor**: End color for gradient effects

## Effect Types

### 1. **set** - Set specific LEDs to a color

```json
{
  "timestampMs": 100,
  "effect": "set",
  "color": "#FF0000",
  "leds": [0, 1, 2, 3, 4, 5]
}
```

### 2. **fill** - Fill all LEDs with a color

```json
{
  "timestampMs": 200,
  "effect": "fill",
  "color": "#00FF00"
}
```

### 3. **clear** - Turn off LEDs

```json
{
  "timestampMs": 300,
  "effect": "clear",
  "leds": [0, 1, 2, 3]  // Optional: specific LEDs, omit to clear all
}
```

### 4. **gradient** - Apply a color gradient across LEDs

```json
{
  "timestampMs": 400,
  "effect": "gradient",
  "startColor": "#FF0000",
  "endColor": "#0000FF",
  "leds": [0, 32, 64, 96, 128, 160, 192, 224]  // Top row of each column
}
```

## Color Format

Colors use 6-digit hex format:
- `#FF0000` - Red
- `#00FF00` - Green
- `#0000FF` - Blue
- `#FFFFFF` - White
- `#000000` - Black (off)
- `#FFA500` - Orange
- `#800080` - Purple

## LED Index Mapping

### Row-by-row indexing:
```
Row 0:   0- 31  (top row)
Row 1:  32- 63
Row 2:  64- 95
Row 3:  96-127
Row 4: 128-159
Row 5: 160-191
Row 6: 192-223
Row 7: 224-255  (bottom row)
```

### Helper formulas:
- LED at (row, col) = `row * 32 + col`
- Row of LED = `index / 32`
- Column of LED = `index % 32`

## Example Patterns

### Simple Chase

```json
{
  "name": "Red Chase",
  "description": "Red light chasing across the matrix",
  "durationMs": 3200,
  "frames": [
    { "timestampMs": 0, "effect": "fill", "color": "#000000" },
    { "timestampMs": 100, "effect": "set", "color": "#FF0000", "leds": [0] },
    { "timestampMs": 200, "effect": "set", "color": "#FF0000", "leds": [1] },
    { "timestampMs": 300, "effect": "set", "color": "#FF0000", "leds": [2] }
    // ... continue for all LEDs
  ]
}
```

### Rainbow Wave

```json
{
  "name": "Rainbow Wave",
  "description": "Rainbow gradient moving across columns",
  "durationMs": 5000,
  "frames": [
    {
      "timestampMs": 0,
      "effect": "gradient",
      "startColor": "#FF0000",
      "endColor": "#FF00FF",
      "leds": [0, 32, 64, 96, 128, 160, 192, 224]
    },
    {
      "timestampMs": 100,
      "effect": "gradient",
      "startColor": "#FF0000",
      "endColor": "#FF00FF",
      "leds": [1, 33, 65, 97, 129, 161, 193, 225]
    }
    // ... continue for all columns
  ]
}
```

### Strobe Effect

```json
{
  "name": "White Strobe",
  "description": "Strobing white light",
  "durationMs": 2000,
  "frames": [
    { "timestampMs": 0, "effect": "fill", "color": "#FFFFFF" },
    { "timestampMs": 100, "effect": "fill", "color": "#000000" },
    { "timestampMs": 200, "effect": "fill", "color": "#FFFFFF" },
    { "timestampMs": 300, "effect": "fill", "color": "#000000" }
  ]
}
```

## Tips

1. **Timing**: Frame timestamps should be synchronized with your music file
2. **Performance**: Limit frames to ~30-60 per second (16-33ms intervals) for smooth animation
3. **File Size**: Keep pattern files reasonable in size; consider repetitive patterns
4. **Testing**: Test patterns on the hardware to ensure timing accuracy
5. **Brightness**: LEDs can be very bright; consider using dimmer colors for indoor use

## Creating Patterns

You can create patterns by:
1. Hand-coding JSON files (for simple patterns)
2. Using a pattern generator script (future enhancement)
3. Recording LED states during a live performance
4. Converting music visualization data to LED patterns
