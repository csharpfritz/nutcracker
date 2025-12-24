import json

# 8 rows x 32 columns LED matrix with serpentine wiring
# Row 0 is top border (green), rows 1-6 are text area (red), row 7 is bottom border (green)

def xy_to_led(x, y, width=32, height=8):
    """Convert x,y coordinates to LED index using serpentine wiring pattern"""
    if x < 0 or x >= width or y < 0 or y >= height:
        return None
    if x % 2 == 0:  # Even columns go down
        return x * height + y
    else:  # Odd columns go up (serpentine)
        return x * height + (height - 1 - y)

# Define 3x5 pixel font (to fit in rows 1-6 with some margin)
FONT_3x5 = {
    'M': [
        "101",
        "111",
        "101",
        "101",
        "101"
    ],
    'E': [
        "111",
        "100",
        "110",
        "100",
        "111"
    ],
    'R': [
        "110",
        "101",
        "110",
        "101",
        "101"
    ],
    'Y': [
        "101",
        "101",
        "010",
        "010",
        "010"
    ],
    'C': [
        "111",
        "100",
        "100",
        "100",
        "111"
    ],
    'H': [
        "101",
        "101",
        "111",
        "101",
        "101"
    ],
    'I': [
        "111",
        "010",
        "010",
        "010",
        "111"
    ],
    'S': [
        "111",
        "100",
        "111",
        "001",
        "111"
    ],
    'T': [
        "111",
        "010",
        "010",
        "010",
        "010"
    ],
    'A': [
        "010",
        "101",
        "111",
        "101",
        "101"
    ],
    ' ': [
        "   ",
        "   ",
        "   ",
        "   ",
        "   "
    ]
}

def create_text_bitmap(text):
    """Create a bitmap for the given text with 1-column spacing between letters"""
    lines = ['', '', '', '', '']
    for i, char in enumerate(text):
        if char.upper() in FONT_3x5:
            letter = FONT_3x5[char.upper()]
            for row in range(5):
                lines[row] += letter[row]
                # Add spacing between letters (except after last letter)
                if i < len(text) - 1:
                    lines[row] += ' '
    return lines

def bitmap_to_led_indices(lines, x_offset, start_row=1):
    """
    Convert bitmap to LED indices at given x_offset
    start_row is the top row where text starts (default 1, leaving row 0 for border)
    """
    leds = []
    for row_idx, line in enumerate(lines):
        y = start_row + row_idx
        for col_idx, char in enumerate(line):
            if char == '1':
                x = col_idx - x_offset
                if 0 <= x < 32:  # Only if visible on display
                    led = xy_to_led(x, y)
                    if led is not None:
                        leds.append(led)
    return sorted(leds)

def get_border_leds():
    """Get LED indices for top (row 0) and bottom (row 7) borders"""
    top = [xy_to_led(x, 0) for x in range(32)]
    bottom = [xy_to_led(x, 7) for x in range(32)]
    return sorted([led for led in top + bottom if led is not None])

def get_text_area_leds():
    """Get all LED indices in the text area (rows 1-6)"""
    leds = []
    for y in range(1, 7):
        for x in range(32):
            led = xy_to_led(x, y)
            if led is not None:
                leds.append(led)
    return sorted(leds)

# Create the scrolling pattern
text = "MERRY CHRISTMAS"
bitmap = create_text_bitmap(text)
text_width = len(bitmap[0])

print(f"Text: {text}")
print(f"Text width: {text_width} columns")
print(f"Display width: 32 columns")
print(f"Total scroll positions: {text_width + 32}")

# Generate frames - optimized to reduce blinking
frames = []
scroll_speed_ms = 120  # milliseconds per column shift
current_time = 0

# Get border LEDs (green, always on)
border_leds = get_border_leds()
text_area_leds = get_text_area_leds()

# Initial setup - borders green, text area black
frames.append({
    "timestampMs": 0,
    "effect": "set",
    "color": "#00FF00",
    "leds": border_leds
})
frames.append({
    "timestampMs": 0,
    "effect": "set",
    "color": "#000000",
    "leds": text_area_leds
})

current_time = scroll_speed_ms
prev_text_leds = set()

# Scroll from right edge to left edge
# Start with text just off-screen to the right (x_offset = -32)
# End when text is just off-screen to the left (x_offset = text_width)
for x_offset in range(-32, text_width + 1):
    # Get text LEDs at current position
    text_leds = set(bitmap_to_led_indices(bitmap, x_offset))
    
    # Calculate which LEDs to turn off (were on, now off)
    leds_to_clear = prev_text_leds - text_leds
    
    # Calculate which LEDs to turn on (were off, now on)
    leds_to_set = text_leds - prev_text_leds
    
    # Only add frames if there are changes
    if leds_to_clear:
        frames.append({
            "timestampMs": current_time,
            "effect": "clear",
            "leds": sorted(list(leds_to_clear))
        })
    
    if leds_to_set:
        frames.append({
            "timestampMs": current_time,
            "effect": "set",
            "color": "#FF0000",
            "leds": sorted(list(leds_to_set))
        })
    
    prev_text_leds = text_leds
    current_time += scroll_speed_ms

# Calculate total duration (add a bit of padding before loop)
total_duration = current_time + 1000

# Create the pattern
pattern = {
    "name": "Merry Christmas Scrolling",
    "description": "Full 'MERRY CHRISTMAS' text scrolling right-to-left with green borders (optimized)",
    "durationMs": total_duration,
    "loop": True,
    "frames": frames
}

# Save to file
output_path = 'Nutcracker/wwwroot/lights/merry-christmas-scrolling.json'
with open(output_path, 'w') as f:
    json.dump(pattern, f, indent=2)

print(f"\nGenerated {len(frames)} frames (optimized)")
print(f"Total duration: {total_duration}ms ({total_duration/1000:.1f} seconds)")
print(f"Scroll speed: {scroll_speed_ms}ms per column")
print(f"Saved to: {output_path}")

# Show a preview of the text at position 0
print("\n=== Preview at x_offset=0 (text starting at left edge) ===")
preview_leds = bitmap_to_led_indices(bitmap, 0)
matrix = [[' ' for _ in range(32)] for _ in range(8)]

# Mark borders
for x in range(32):
    matrix[0][x] = 'G'
    matrix[7][x] = 'G'

# Mark text
for led in preview_leds:
    for y in range(8):
        for x in range(32):
            if xy_to_led(x, y) == led:
                matrix[y][x] = 'R'

for i, row in enumerate(matrix):
    print(f"Row {i}: {''.join(row)}")

