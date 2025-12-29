import librosa
import numpy as np

print("Loading audio file...")
y, sr = librosa.load('Nutcracker/wwwroot/music/Bruce Springsteen - Santa Claus Is Comin To Town (Official Audio).mp3')
duration = librosa.get_duration(y=y, sr=sr)

print(f"Duration: {duration:.2f}s ({int(duration * 1000)}ms)")
print()
print("=" * 80)
print("TIMESTAMP FINDER - Listen to the song and note when Bruce sings:")
print("'Santa Claus is coming to town'")
print("=" * 80)
print()

# Create 10-second markers throughout the song
print("Use these time markers to help identify the exact moments:")
print()

for seconds in range(0, int(duration) + 1, 10):
    minutes = seconds // 60
    secs = seconds % 60
    milliseconds = seconds * 1000
    print(f"{minutes}:{secs:02d} ({milliseconds:5d}ms) | ", end="")
    
    # Add visual marker every 30 seconds
    if seconds % 30 == 0:
        print("*** CHECKPOINT ***")
    else:
        print()

print()
print("=" * 80)
print("INSTRUCTIONS:")
print("=" * 80)
print("1. Play the song: Nutcracker/wwwroot/music/Bruce Springsteen...")
print("2. Listen for each time Bruce sings 'Santa Claus is coming to town'")
print("3. Note the timestamp from the markers above (look at your player's time)")
print("4. Write down the timestamps in milliseconds")
print()
print("EXAMPLE FORMAT:")
print("chorus_times = [")
print("    23500,   # First 'Santa Claus...' at 0:23")
print("    48200,   # Second at 0:48")
print("    # ... etc")
print("]")
print()
print("Alternatively, you can listen and tell me:")
print("'The first one is at 0:23, second at 0:48, etc.'")
print()
print("Then I'll update the lightshow with the exact times!")
