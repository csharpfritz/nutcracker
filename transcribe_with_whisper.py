import whisper
import json

print("Loading Whisper model (this may take a moment)...")
model = whisper.load_model("base")  # Use "base" for speed, or "small"/"medium" for better accuracy

print("Transcribing audio with timestamps...")
audio_path = 'Nutcracker/wwwroot/music/Bruce Springsteen - Santa Claus Is Comin To Town (Official Audio).mp3'

result = model.transcribe(
    audio_path,
    word_timestamps=True,
    language="en"
)

print("\n" + "=" * 80)
print("FULL TRANSCRIPTION WITH TIMESTAMPS")
print("=" * 80)

# Find all instances where "Santa Claus" is mentioned
santa_timestamps = []

for segment in result['segments']:
    print(f"\n[{segment['start']:.2f}s - {segment['end']:.2f}s]")
    print(f"  {segment['text']}")
    
    # Check if this segment contains "Santa Claus"
    text_lower = segment['text'].lower()
    if 'santa claus' in text_lower or 'santa clause' in text_lower:
        timestamp_ms = int(segment['start'] * 1000)
        santa_timestamps.append({
            'time_s': segment['start'],
            'time_ms': timestamp_ms,
            'text': segment['text'].strip()
        })

print("\n" + "=" * 80)
print("FOUND 'SANTA CLAUS' TIMESTAMPS")
print("=" * 80)

if santa_timestamps:
    print("\nTimestamps where 'Santa Claus' is sung:\n")
    
    for i, item in enumerate(santa_timestamps, 1):
        minutes = int(item['time_s'] // 60)
        seconds = int(item['time_s'] % 60)
        print(f"{i}. {minutes}:{seconds:02d} ({item['time_ms']:6d}ms) - \"{item['text']}\"")
    
    print("\n" + "-" * 80)
    print("PYTHON CODE FOR LIGHTSHOW:")
    print("-" * 80)
    print("\nchorus_times = [")
    for item in santa_timestamps:
        minutes = int(item['time_s'] // 60)
        seconds = int(item['time_s'] % 60)
        print(f"    {item['time_ms']},   # {minutes}:{seconds:02d} - \"{item['text'][:40]}...\"")
    print("]")
    
    # Save to file
    with open('santa_timestamps.json', 'w') as f:
        json.dump(santa_timestamps, f, indent=2)
    
    print("\n✓ Timestamps saved to santa_timestamps.json")
else:
    print("\nNo 'Santa Claus' mentions found. Showing all segments above for manual review.")

print("\n" + "=" * 80)
