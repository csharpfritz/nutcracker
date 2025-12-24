import json

# 8x32 LED matrix - landscape orientation
# Each letter is 5 pixels wide with 1 pixel spacing
# Font is 5 pixels tall (using rows 1-5, leaving row 0 and 7 for spacing)

# Define letters as 5x5 bitmaps (top to bottom, left to right)
LETTERS = {
    'M': [
        "1   1",
        "11 11",
        "1 1 1",
        "1   1",
        "1   1"
    ],
    'E': [
        "11111",
        "1    ",
        "1111 ",
        "1    ",
        "11111"
    ],
    'R': [
        "1111 ",
        "1   1",
        "1111 ",
        "1 1  ",
        "1  1 "
    ],
    'Y': [
        "1   1",
        "1   1",
        " 1 1 ",
        "  1  ",
        "  1  "
    ],
    'X': [
        "1   1",
        " 1 1 ",
        "  1  ",
        " 1 1 ",
        "1   1"
    ],
    'A': [
        " 111 ",
        "1   1",
        "11111",
        "1   1",
        "1   1"
    ],
    'S': [
        " 1111",
        "1    ",
        " 111 ",
        "    1",
        "1111 "
    ],
    ' ': [
        "  ",
        "  ",
        "  ",
        "  ",
        "  "
    ]
}

def create_text_bitmap(text):
    """Create a bitmap for the given text"""
    lines = ['', '', '', '', '']
    for char in text:
        if char in LETTERS:
            letter = LETTERS[char]
            for i in range(5):
                lines[i] += letter[i] + ' '  # Add spacing between letters
    return lines

def bitmap_to_leds(lines, offset, width=32, start_row=1):
    """Convert bitmap lines to LED indices with horizontal offset"""
    leds = []
    for row_idx, line in enumerate(lines):
        row = start_row + row_idx
        for col_idx, char in enumerate(line):
            if char == '1':
                display_col = col_idx - offset
                if 0 <= display_col < width:
                    led_index = row * 32 + display_col
                    leds.append(led_index)
    return sorted(leds)

# Create the scrolling pattern
text = "MERRY XMAS"
bitmap = create_text_bitmap(text)

# Calculate text width
text_width = len(bitmap[0])
print(f"Text width: {text_width} pixels")

# Generate frames for scrolling from right to left
frames = []
colors = ["#FF0000", "#00FF00"]  # Alternate red and green

# Start with blank
frames.append({
    "timestampMs": 0,
    "effect": "fill",
    "color": "#000000"
})

# Create scrolling animation
frame_delay = 100  # milliseconds between frames
current_time = 50

# Scroll from right (offset = -32) to left (offset = text_width)
for offset in range(-32, text_width + 1):
    # Clear frame
    frames.append({
        "timestampMs": current_time,
        "effect": "fill",
        "color": "#000000"
    })
    current_time += frame_delay
    
    # Set LEDs for current position
    leds = bitmap_to_leds(bitmap, offset)
    if leds:  # Only add frame if there are LEDs to light
        color = colors[0] if offset % 4 < 2 else colors[1]  # Alternate colors
        frames.append({
            "timestampMs": current_time,
            "effect": "set",
            "color": color,
            "leds": leds
        })
    
    current_time += frame_delay

# Final clear
frames.append({
    "timestampMs": current_time,
    "effect": "fill",
    "color": "#000000"
})

# Create the pattern
pattern = {
    "name": "Merry Christmas Scrolling Text",
    "description": "Scrolling MERRY XMAS text in landscape orientation",
    "durationMs": current_time + 1000,
    "frames": frames
}

# Save to file
output_path = 'D:/Nutcracker/Nutcracker/wwwroot/lights/merry-christmas-scrolling.json'
with open(output_path, 'w') as f:
    json.dump(pattern, f, indent=2)

print(f"\nGenerated {len(frames)} frames")
print(f"Total duration: {pattern['durationMs']}ms")
print(f"Saved to: {output_path}")

# Show a preview
print("\nPreview of text at offset 5:")
preview_leds = bitmap_to_leds(bitmap, 5)
matrix = [[' ' for _ in range(32)] for _ in range(8)]
for led in preview_leds:
    row = led // 32
    col = led % 32
    if 0 <= row < 8 and 0 <= col < 32:
        matrix[row][col] = '#'

for i, row in enumerate(matrix):
    print(f"Row {i}: {''.join(row)}")
