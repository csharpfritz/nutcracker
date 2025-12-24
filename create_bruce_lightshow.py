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

# Energy analysis
hop_length = 512
energy = librosa.feature.rms(y=y, hop_length=hop_length)[0]
energy_times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=hop_length)

# Normalize energy to 0-1
energy_normalized = (energy - energy.min()) / (energy.max() - energy.min())

def get_energy_at_time(time_ms):
    """Get normalized energy at a specific time."""
    time_s = time_ms / 1000
    idx = np.searchsorted(energy_times, time_s)
    if idx >= len(energy_normalized):
        idx = len(energy_normalized) - 1
    return float(energy_normalized[idx])

# Generate all bottom row LEDs (y=7)
bottom_row = [xy_to_led(x, 7) for x in range(WIDTH)]

# Generate all top row LEDs (y=0)
top_row = [xy_to_led(x, 0) for x in range(WIDTH)]

# Generate alternating columns (even columns)
even_columns = []
for x in range(0, WIDTH, 2):
    for y in range(HEIGHT):
        even_columns.append(xy_to_led(x, y))

# Generate alternating columns (odd columns)
odd_columns = []
for x in range(1, WIDTH, 2):
    for y in range(HEIGHT):
        odd_columns.append(xy_to_led(x, y))

# Create lightshow frames
frames = []

# Start with black
frames.append({
    "timestampMs": 0,
    "effect": "fill",
    "color": "#000000"
})

print("Generating frames...")

# Generate beat-synced animation with smoother transitions
pattern_cycle = 0
last_big_effect = 0

for i, beat_ms in enumerate(beat_times_ms):
    if beat_ms > duration_ms:
        break
    
    energy = get_energy_at_time(beat_ms)
    pattern_cycle = i % 8
    
    # Avoid effects too close together
    if beat_ms - last_big_effect < 200:
        continue
    
    # Every beat: pulse the bottom or top row (no full clears)
    if i % 2 == 0:  # Strong beats
        # Red pulse on bottom
        frames.append({
            "timestampMs": beat_ms,
            "effect": "set",
            "color": "#CC0000",
            "leds": bottom_row
        })
        
        # Fade out (dim, don't clear completely)
        frames.append({
            "timestampMs": beat_ms + 150,
            "effect": "set",
            "color": "#330000",
            "leds": bottom_row
        })
    else:  # Weak beats
        # White pulse on top
        frames.append({
            "timestampMs": beat_ms,
            "effect": "set",
            "color": "#CCCCCC",
            "leds": top_row
        })
        
        # Fade out
        frames.append({
            "timestampMs": beat_ms + 150,
            "effect": "set",
            "color": "#333333",
            "leds": top_row
        })
    
    # Every 16 beats: bigger flash (but don't use fill)
    if i > 0 and i % 16 == 0:
        last_big_effect = beat_ms
        # Flash borders bright
        border_leds = top_row + bottom_row
        frames.append({
            "timestampMs": beat_ms,
            "effect": "set",
            "color": "#CC0000",
            "leds": border_leds
        })
        
        frames.append({
            "timestampMs": beat_ms + 100,
            "effect": "set",
            "color": "#CCCCCC",
            "leds": border_leds
        })
        
        frames.append({
            "timestampMs": beat_ms + 200,
            "effect": "set",
            "color": "#660000",
            "leds": border_leds
        })
    
    # Every 32 beats: column wave effect
    if i > 0 and i % 32 == 0 and i < len(beat_times_ms) - 16:
        last_big_effect = beat_ms
        sweep_start = beat_ms
        # Wave effect - light up columns progressively
        for col in range(0, WIDTH, 2):
            sweep_time = sweep_start + int(col * 80)
            if sweep_time < duration_ms:
                col_leds = [xy_to_led(col, y) for y in range(HEIGHT)]
                if col + 1 < WIDTH:
                    col_leds.extend([xy_to_led(col + 1, y) for y in range(HEIGHT)])
                
                frames.append({
                    "timestampMs": sweep_time,
                    "effect": "set",
                    "color": "#CC0000" if col % 4 == 0 else "#CCCCCC",
                    "leds": col_leds
                })
                
                # Dim previous columns
                if col > 0:
                    prev_leds = [xy_to_led(col - 2, y) for y in range(HEIGHT)]
                    if col - 1 >= 0:
                        prev_leds.extend([xy_to_led(col - 1, y) for y in range(HEIGHT)])
                    
                    frames.append({
                        "timestampMs": sweep_time + 40,
                        "effect": "set",
                        "color": "#330000",
                        "leds": prev_leds
                    })
    
    # Alternating effect during very high energy sections
    if energy > 0.75 and i % 6 == 0:
        last_big_effect = beat_ms
        target_columns = even_columns if pattern_cycle % 2 == 0 else odd_columns
        frames.append({
            "timestampMs": beat_ms,
            "effect": "set",
            "color": "#CC0000",
            "leds": target_columns
        })
        
        frames.append({
            "timestampMs": beat_ms + 250,
            "effect": "set",
            "color": "#330000",
            "leds": target_columns
        })

# Final frame - fade to black
frames.append({
    "timestampMs": duration_ms,
    "effect": "fill",
    "color": "#000000"
})

# Sort frames by timestamp
frames.sort(key=lambda x: x["timestampMs"])

# Remove duplicate timestamps (keep last one for each timestamp)
unique_frames = []
seen_times = set()
for frame in reversed(frames):
    if frame["timestampMs"] not in seen_times:
        unique_frames.append(frame)
        seen_times.add(frame["timestampMs"])

unique_frames.reverse()

print(f"Generated {len(unique_frames)} frames")

# Create lightshow JSON
lightshow = {
    "name": "Bruce Springsteen - Santa Claus Is Comin' To Town",
    "description": f"High-energy rock lightshow with strong beat pulses, column sweeps, and dynamic red/white patterns. BPM: {float(tempo):.1f}, Beats: {len(beat_times_ms)}",
    "durationMs": duration_ms,
    "frames": unique_frames
}

# Save to file
output_path = 'Nutcracker/wwwroot/lights/bruce-springsteen-santa-claus.json'
with open(output_path, 'w') as f:
    json.dump(lightshow, f, indent=2)

print(f"✓ Saved lightshow to {output_path}")
print(f"  Duration: {duration_ms}ms ({duration:.2f}s)")
print(f"  BPM: {float(tempo):.1f}")
print(f"  Frames: {len(unique_frames)}")
print(f"  Beats: {len(beat_times_ms)}")
