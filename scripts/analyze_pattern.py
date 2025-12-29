import json

# Load the pattern
with open('D:/Nutcracker/Nutcracker/wwwroot/lights/merry-christmas-static.json') as f:
    pattern = json.load(f)

# Matrix is 32 cols x 8 rows
def led_to_xy(led):
    row = led // 32
    col = led % 32
    return (col, row)

print("Analyzing 'MERRY XMAS' scrolling pattern")
print("Matrix: 32 columns x 8 rows")
print("=" * 80)
print()

# Analyze several frames to see the pattern
for frame_idx in [1, 3, 5, 7]:
    frame = pattern['frames'][frame_idx]
    print(f"Frame at {frame['timestampMs']}ms:")
    
    # Create a visual representation
    matrix = [[' ' for _ in range(32)] for _ in range(8)]
    for led in frame['leds']:
        col, row = led_to_xy(led)
        if 0 <= row < 8 and 0 <= col < 32:
            matrix[row][col] = '#'
    
    print('Visual (top to bottom):')
    for i, row in enumerate(matrix):
        print(f"Row {i}: {''.join(row)}")
    print()
