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

# Generate beat-synced animation
pattern_cycle = 0
for i, beat_ms in enumerate(beat_times_ms):
    if beat_ms > duration_ms:
        break
    
    energy = get_energy_at_time(beat_ms)
    pattern_cycle = i % 8
    
    # Every beat: pulse the bottom row
    if i % 2 == 0:  # Strong beats
        # Red flash on bottom
        frames.append({
            "timestampMs": beat_ms,
            "effect": "set",
            "color": "#CC0000",
            "leds": bottom_row
        })
        
        # Fade out
        frames.append({
            "timestampMs": beat_ms + 100,
            "effect": "set",
            "color": "#660000",
            "leds": bottom_row
        })
        
        frames.append({
            "timestampMs": beat_ms + 200,
            "effect": "clear",
            "leds": bottom_row
        })
    else:  # Weak beats
        # White flash on top
        frames.append({
            "timestampMs": beat_ms,
            "effect": "set",
            "color": "#CCCCCC",
            "leds": top_row
        })
        
        frames.append({
            "timestampMs": beat_ms + 100,
            "effect": "clear",
            "leds": top_row
        })
    
    # Every 8 beats: big visual effect
    if i > 0 and i % 16 == 0:
        # Full flash
        frames.append({
            "timestampMs": beat_ms,
            "effect": "fill",
            "color": "#CC0000"
        })
        
        frames.append({
            "timestampMs": beat_ms + 150,
            "effect": "fill",
            "color": "#CCCCCC"
        })
        
        frames.append({
            "timestampMs": beat_ms + 300,
            "effect": "fill",
            "color": "#000000"
        })
    
    # Every 32 beats: column sweep effect
    if i > 0 and i % 32 == 0 and i < len(beat_times_ms) - 16:
        sweep_start = beat_ms
        # Sweep columns left to right over 8 beats
        for col in range(0, WIDTH, 4):
            sweep_time = sweep_start + int(col * 100)
            if sweep_time < duration_ms:
                col_leds = [xy_to_led(col + offset, y) for offset in range(min(4, WIDTH - col)) for y in range(HEIGHT)]
                frames.append({
                    "timestampMs": sweep_time,
                    "effect": "set",
                    "color": "#CC0000" if col % 8 == 0 else "#CCCCCC",
                    "leds": col_leds
                })
        
        # Clear after sweep
        clear_time = sweep_start + 3200
        if clear_time < duration_ms:
            frames.append({
                "timestampMs": clear_time,
                "effect": "fill",
                "color": "#000000"
            })
    
    # Alternating columns effect during high energy sections
    if energy > 0.7 and i % 4 == 0:
        frames.append({
            "timestampMs": beat_ms,
            "effect": "set",
            "color": "#CC0000",
            "leds": even_columns if pattern_cycle % 2 == 0 else odd_columns
        })
        
        frames.append({
            "timestampMs": beat_ms + 200,
            "effect": "fill",
            "color": "#000000"
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
