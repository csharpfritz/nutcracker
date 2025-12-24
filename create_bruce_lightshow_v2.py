import librosa
import numpy as np
import json

# LED matrix configuration
WIDTH = 32
HEIGHT = 8

def xy_to_led(x, y, width=32, height=8):
    """Convert matrix coordinates to LED index for serpentine wiring."""
    if x % 2 == 0:  # Even columns go DOWN (0→7)
        return x * height + y
    else:           # Odd columns go UP (7→0)
        return x * height + (height - 1 - y)

# 5x7 pixel LARGE font for letters (uses full height minus borders)
FONT_5x7 = {
    'S': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0]
    ],
    'A': [
        [0, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1]
    ],
    'N': [
        [1, 0, 0, 0, 1],
        [1, 1, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1]
    ],
    'T': [
        [1, 1, 1, 1, 1],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0]
    ]
}

def render_text(text, start_x, color):
    """Render large text on the LED matrix, returns frame data."""
    leds = []
    x_offset = start_x
    for char in text:
        if char in FONT_5x7:
            font_data = FONT_5x7[char]
            for row_idx in range(7):
                for col_idx in range(5):
                    if font_data[row_idx][col_idx] == 1:
                        x = x_offset + col_idx
                        y = row_idx + 0  # Use y=0 to y=6 (leave y=7 for bottom border)
                        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                            leds.append(xy_to_led(x, y))
            x_offset += 6  # 5 pixel width + 1 space
    return {
        "effect": "set",
        "color": color,
        "leds": leds
    }

def create_sleigh(x_pos, color):
    """Create a traditional curved Santa sleigh at given x position (10 pixels wide, 6 tall)."""
    leds = []
    # Traditional sleigh silhouette with curved front and runners
    # Inspired by classic Christmas sleigh shape
    # 10 pixels wide x 6 pixels tall
    shape = [
        [0, 0, 1, 1, 1, 0, 0, 0, 1, 1],  # Curved top front and back curl
        [0, 1, 1, 1, 1, 1, 0, 1, 1, 0],  # Upper body curve
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0],  # Mid body
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],  # Lower body
        [0, 1, 1, 0, 0, 0, 1, 1, 0, 0],  # Runners top
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]   # Runners bottom (curved)
    ]
    
    for row_idx, row in enumerate(shape):
        for col_idx, pixel in enumerate(row):
            if pixel == 1:
                x = x_pos + col_idx
                y = 1 + row_idx  # Start at y=1 (6 rows tall)
                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    leds.append(xy_to_led(x, y))
    return leds

def create_star(x, y):
    """Create a star shape (cross pattern)."""
    leds = []
    # Center pixel
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        leds.append(xy_to_led(x, y))
    # Cross arms
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
            leds.append(xy_to_led(nx, ny))
    return leds

def create_snowflake(x, y):
    """Create a snowflake pattern."""
    leds = []
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        leds.append(xy_to_led(x, y))
    # 8 directions
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                leds.append(xy_to_led(nx, ny))
    return leds

# Load audio and analyze
print("Loading audio file...")
y, sr = librosa.load('Nutcracker/wwwroot/music/Bruce Springsteen - Santa Claus Is Comin To Town (Official Audio).mp3')
duration = librosa.get_duration(y=y, sr=sr)
duration_ms = int(duration * 1000)

print(f"Duration: {duration:.2f}s ({duration_ms}ms)")

# Beat detection
print("Detecting beats...")
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beats, sr=sr)
beat_times_ms = (beat_times * 1000).astype(int).tolist()

print(f"BPM: {float(tempo):.1f}")
print(f"Beats detected: {len(beat_times_ms)}")

# Estimate song structure (this is approximate - you may want to adjust times based on listening)
# Typical song structure: Intro -> Verse 1 -> Chorus 1 -> Verse 2 -> Chorus 2 -> Bridge -> Final Chorus
# "Santa Claus is coming to town" appears in choruses
# Based on Bruce Springsteen's version structure and BPM of 143.6

# EXACT chorus times from Whisper AI transcription with word-level timestamps
# These are the precise moments when Bruce sings "Santa Claus is coming to town"
chorus_times = [
    57580,   # 0:57 - First "Santa Claus is coming to town"
    61540,   # 1:01 - Second repetition
    65420,   # 1:05 - Third repetition
    81760,   # 1:21 - Fourth
    85180,   # 1:25 - Fifth
    89000,   # 1:29 - Sixth
    122820,  # 2:02 - Seventh
    125960,  # 2:05 - Eighth
    128940,  # 2:08 - Ninth
    145600,  # 2:25 - Tenth
    155700   # 2:35 - Eleventh (final in first half)
]

# Generate all bottom row LEDs (y=7)
bottom_row = [xy_to_led(x, 7) for x in range(WIDTH)]
top_row = [xy_to_led(x, 0) for x in range(WIDTH)]

# Create lightshow frames
frames = []

# Start with black
frames.append({
    "timestampMs": 0,
    "effect": "fill",
    "color": "#000000"
})

print("Generating creative frames...")

# Track what effects we've used to avoid repetition
last_sleigh = 0
last_text = 0
last_stars = 0

for i, beat_ms in enumerate(beat_times_ms):
    if beat_ms > duration_ms:
        break
    
    pattern_cycle = i % 32
    
    # Check if we're near a chorus time (within 2 seconds)
    near_chorus = any(abs(beat_ms - ct) < 3000 for ct in chorus_times)
    in_chorus = any(abs(beat_ms - ct) < 10000 for ct in chorus_times)
    
    # SANTA text display during chorus (when he sings "Santa Claus")
    # Display SANTA for each chorus with big, visible text
    if near_chorus and beat_ms - last_text > 10000:
        last_text = beat_ms
        
        # Clear screen first
        frames.append({
            "timestampMs": beat_ms,
            "effect": "fill",
            "color": "#000000"
        })
        
        # Flash "SANTA" 4 times in RED with growing intensity
        for flash in range(4):
            colors = ["#660000", "#990000", "#CC0000", "#FF0000"]
            text_frame = render_text("SANTA", 1, colors[flash])
            frames.append({
                "timestampMs": beat_ms + 100 + flash * 400,
                **text_frame
            })
            # Brief dim (don't fully clear)
            if flash < 3:
                frames.append({
                    "timestampMs": beat_ms + 300 + flash * 400,
                    "effect": "set",
                    "color": "#330000",
                    "leds": text_frame["leds"]
                })
        
        # Keep SANTA visible in bright red for 2 seconds
        text_frame = render_text("SANTA", 1, "#FF0000")
        frames.append({
            "timestampMs": beat_ms + 1700,
            **text_frame
        })
        
        # Then switch to white
        text_frame_white = render_text("SANTA", 1, "#FFFFFF")
        frames.append({
            "timestampMs": beat_ms + 3000,
            **text_frame_white
        })
        
        # Slow fade out
        for fade_step in range(4):
            fade_colors = ["#CCCCCC", "#999999", "#666666", "#333333"]
            text_frame_fade = render_text("SANTA", 1, fade_colors[fade_step])
            frames.append({
                "timestampMs": beat_ms + 4000 + fade_step * 400,
                **text_frame_fade
            })
        
        # Final clear
        frames.append({
            "timestampMs": beat_ms + 6000,
            "effect": "fill",
            "color": "#000000"
        })
        
        continue
    
    # Sleigh animation every ~12 seconds when NOT in chorus
    if not in_chorus and beat_ms - last_sleigh > 12000 and i > 0 and i % 25 == 0:
        last_sleigh = beat_ms
        # Traditional curved sleigh moves from left to right over 5 seconds
        for x in range(-10, WIDTH + 10, 2):
            sleigh_time = beat_ms + int((x + 10) * 120)
            if sleigh_time < duration_ms:
                sleigh_leds = create_sleigh(x, "#CC0000")
                if sleigh_leds:
                    frames.append({
                        "timestampMs": sleigh_time,
                        "effect": "set",
                        "color": "#CC0000",
                        "leds": sleigh_leds
                    })
                    
                    # Golden sparkles behind sleigh (3 sparkles at different heights)
                    if x > 3:
                        sparkle_leds = create_star(x - 4, 2) + create_star(x - 3, 4) + create_star(x - 4, 6)
                        frames.append({
                            "timestampMs": sleigh_time,
                            "effect": "set",
                            "color": "#FFCC00",
                            "leds": sparkle_leds
                        })
                    
                    # Clear previous position
                    if x > 4:
                        prev_sleigh = create_sleigh(x - 4, "#000000")
                        frames.append({
                            "timestampMs": sleigh_time + 50,
                            "effect": "set",
                            "color": "#000000",
                            "leds": prev_sleigh
                        })
        continue
    
    # Falling snowflakes every ~15 seconds
    if beat_ms - last_stars > 15000 and i > 0 and i % 30 == 0:
        last_stars = beat_ms
        # Multiple snowflakes falling
        for flake in range(5):
            x_pos = (flake * 7 + 2) % WIDTH
            for fall_step in range(HEIGHT - 1):
                fall_time = beat_ms + flake * 200 + fall_step * 300
                if fall_time < duration_ms:
                    flake_leds = create_star(x_pos, fall_step)
                    frames.append({
                        "timestampMs": fall_time,
                        "effect": "set",
                        "color": "#CCCCCC",
                        "leds": flake_leds
                    })
                    # Clear previous position
                    if fall_step > 0:
                        prev_leds = create_star(x_pos, fall_step - 1)
                        frames.append({
                            "timestampMs": fall_time + 50,
                            "effect": "set",
                            "color": "#000000",
                            "leds": prev_leds
                        })
        continue
    
    # Column wave effects on strong beats (every 8 beats)
    if i % 8 == 0:
        color = "#CC0000" if (i // 8) % 2 == 0 else "#00CC00"
        for col in range(WIDTH):
            col_time = beat_ms + col * 60
            if col_time < duration_ms:
                col_leds = [xy_to_led(col, y) for y in range(HEIGHT)]
                frames.append({
                    "timestampMs": col_time,
                    "effect": "set",
                    "color": color,
                    "leds": col_leds
                })
                # Trail effect
                if col > 0:
                    prev_col = [xy_to_led(col - 1, y) for y in range(HEIGHT)]
                    frames.append({
                        "timestampMs": col_time + 30,
                        "effect": "set",
                        "color": "#330000",
                        "leds": prev_col
                    })
        continue
    
    # Border pulse on every 4th beat
    if i % 4 == 0:
        border_leds = top_row + bottom_row
        frames.append({
            "timestampMs": beat_ms,
            "effect": "set",
            "color": "#00CC00",
            "leds": border_leds
        })
        frames.append({
            "timestampMs": beat_ms + 200,
            "effect": "set",
            "color": "#003300",
            "leds": border_leds
        })
        continue
    
    # Corner stars on regular beats
    if i % 2 == 0:
        corners = []
        for x, y in [(1, 1), (WIDTH-2, 1), (1, HEIGHT-2), (WIDTH-2, HEIGHT-2)]:
            corners.extend(create_star(x, y))
        frames.append({
            "timestampMs": beat_ms,
            "effect": "set",
            "color": "#CCCC00",
            "leds": corners
        })
        frames.append({
            "timestampMs": beat_ms + 150,
            "effect": "set",
            "color": "#333300",
            "leds": corners
        })

# Final frame - fade to black
frames.append({
    "timestampMs": duration_ms,
    "effect": "fill",
    "color": "#000000"
})

# Sort frames by timestamp
frames.sort(key=lambda x: x["timestampMs"])

print(f"Generated {len(frames)} frames")

# Create lightshow JSON
lightshow = {
    "name": "Bruce Springsteen - Santa Claus Is Comin' To Town",
    "description": f"Creative holiday lightshow with SANTA text, sleigh animations, falling snowflakes, and dynamic effects. BPM: {float(tempo):.1f}",
    "durationMs": duration_ms,
    "frames": frames
}

# Save to file
output_path = 'Nutcracker/wwwroot/lights/bruce-springsteen-santa-claus.json'
with open(output_path, 'w') as f:
    json.dump(lightshow, f, indent=2)

print(f"✓ Saved creative lightshow to {output_path}")
print(f"  Duration: {duration_ms}ms ({duration:.2f}s)")
print(f"  BPM: {float(tempo):.1f}")
print(f"  Frames: {len(frames)}")
print(f"  Features: SANTA text, sleigh animations, snowflakes, waves, corner stars")
