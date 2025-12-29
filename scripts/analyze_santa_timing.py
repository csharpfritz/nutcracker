import librosa
import numpy as np

# Load audio
print("Loading audio file...")
y, sr = librosa.load('Nutcracker/wwwroot/music/Bruce Springsteen - Santa Claus Is Comin To Town (Official Audio).mp3')
duration = librosa.get_duration(y=y, sr=sr)

print(f"Duration: {duration:.2f}s")

# Beat detection
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beats, sr=sr)

print(f"BPM: {float(tempo):.1f}")

# Get spectral features to identify vocal sections
hop_length = 512
chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]

# Normalize
rms_normalized = (rms - rms.min()) / (rms.max() - rms.min())

# Identify high-energy sections (likely choruses)
threshold = 0.6
high_energy = rms_normalized > threshold

# Find continuous high-energy sections
sections = []
in_section = False
start_time = 0

times = librosa.frames_to_time(np.arange(len(rms_normalized)), sr=sr, hop_length=hop_length)

for i, is_high in enumerate(high_energy):
    if is_high and not in_section:
        start_time = times[i]
        in_section = True
    elif not is_high and in_section:
        end_time = times[i]
        # Only consider sections longer than 5 seconds (likely choruses)
        if end_time - start_time > 5:
            sections.append((start_time, end_time))
        in_section = False

print(f"\nHigh-energy sections (likely choruses/hook phrases):")
print("=" * 60)

for i, (start, end) in enumerate(sections, 1):
    print(f"Section {i}: {start:.2f}s - {end:.2f}s (duration: {end-start:.1f}s)")
    print(f"  Timestamp: ~{int(start*1000)}ms")

# Based on typical song structure, the title phrase "Santa Claus is coming to town"
# usually appears at:
# 1. After the intro (first chorus) - around 20-30s
# 2. After first verse - around 50-70s  
# 3. Multiple times in final section - 180s onwards

print("\n" + "=" * 60)
print("RECOMMENDED TIMINGS for 'SANTA' text display:")
print("=" * 60)
print("Based on high-energy sections, use these times (in milliseconds):")
print()

# Filter sections that are likely chorus/hook moments
likely_chorus_times = []
for start, end in sections:
    # Choruses typically happen after intro and are spaced out
    if start > 15:  # After intro
        likely_chorus_times.append(int(start * 1000))

# Show the first several occurrences
for i, time_ms in enumerate(likely_chorus_times[:8], 1):
    print(f"  Chorus {i}: {time_ms} ms ({time_ms/1000:.1f}s)")
