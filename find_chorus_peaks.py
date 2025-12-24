import librosa
import numpy as np

print("Loading audio file...")
y, sr = librosa.load('Nutcracker/wwwroot/music/Bruce Springsteen - Santa Claus Is Comin To Town (Official Audio).mp3')
duration = librosa.get_duration(y=y, sr=sr)

print(f"Duration: {duration:.2f}s")
print()

# Get vocal/harmonic energy (separates vocals from instruments)
print("Analyzing vocal energy...")
harmonic, percussive = librosa.effects.hpss(y)

# Get RMS energy of harmonic (vocal) component
hop_length = 512
rms = librosa.feature.rms(y=harmonic, hop_length=hop_length)[0]
times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

# Normalize
rms_norm = (rms - rms.min()) / (rms.max() - rms.min())

# Find peaks in vocal energy (likely chorus/hook moments)
from scipy.signal import find_peaks

# Find peaks that are prominent and spaced out (at least 15 seconds apart)
peaks, properties = find_peaks(
    rms_norm, 
    height=0.7,  # High energy
    distance=int(15 * sr / hop_length)  # At least 15 seconds apart
)

peak_times = times[peaks]
peak_heights = rms_norm[peaks]

print("\n" + "=" * 80)
print("HIGH-ENERGY VOCAL PEAKS (Likely chorus/hook moments)")
print("=" * 80)
print("\nThese are the most likely times when 'Santa Claus...' is sung:")
print()

chorus_candidates = []
for i, (time, height) in enumerate(zip(peak_times, peak_heights), 1):
    time_ms = int(time * 1000)
    minutes = int(time // 60)
    seconds = int(time % 60)
    chorus_candidates.append(time_ms)
    print(f"{i}. {minutes}:{seconds:02d} ({time_ms:6d}ms) - Energy: {height:.2f}")

print("\n" + "=" * 80)
print("RECOMMENDED CHORUS TIMES:")
print("=" * 80)
print("\nchorus_times = [")
for time_ms in chorus_candidates:
    minutes = int((time_ms / 1000) // 60)
    seconds = int((time_ms / 1000) % 60)
    print(f"    {time_ms},   # {minutes}:{seconds:02d}")
print("]")

print("\n" + "=" * 80)
print("NEXT STEPS:")
print("=" * 80)
print("1. Listen to the song at these timestamps")
print("2. Adjust times by ±5 seconds if needed to sync with actual lyrics")
print("3. Let me know which times are correct or need adjustment")
