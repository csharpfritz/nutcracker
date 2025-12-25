#!/usr/bin/env python3
"""
Analyze Wizards in Winter MP3 to extract beat timings and energy levels
"""

import librosa
import numpy as np
import json

def analyze_audio(file_path):
    """Analyze the audio file for beats and energy."""
    print(f"Loading audio: {file_path}")
    y, sr = librosa.load(file_path)
    
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"Duration: {duration:.2f} seconds")
    
    # Estimate tempo and beats
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    
    # Handle tempo being either scalar or array
    tempo_val = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
    
    print(f"Estimated tempo: {tempo_val:.1f} BPM")
    print(f"Detected {len(beat_times)} beats")
    
    # Get onset strength (for finding strong beats)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_times = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr)
    
    # Find peaks in onset strength (strong beats)
    from scipy.signal import find_peaks
    peaks, properties = find_peaks(onset_env, height=np.mean(onset_env), distance=sr//512)
    peak_times = librosa.frames_to_time(peaks, sr=sr)
    peak_strengths = properties['peak_heights']
    
    print(f"Found {len(peak_times)} strong beats/onsets")
    
    # Compute energy envelope for sections
    hop_length = 512
    frame_length = 2048
    energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    energy_times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=hop_length)
    
    # Save beat data
    beat_data = {
        'duration_ms': int(duration * 1000),
        'tempo': tempo_val,
        'beat_times_ms': [int(t * 1000) for t in beat_times],
        'strong_beats_ms': [int(t * 1000) for t in peak_times],
        'strong_beat_strengths': [float(s) for s in peak_strengths],
        'energy_envelope': {
            'times_ms': [int(t * 1000) for t in energy_times],
            'values': [float(e) for e in energy]
        }
    }
    
    output_file = 'wizards_beat_data.json'
    with open(output_file, 'w') as f:
        json.dump(beat_data, f, indent=2)
    
    print(f"\nSaved beat data to: {output_file}")
    
    # Print some example beats
    print(f"\nFirst 20 strong beats (ms):")
    for i, (t, s) in enumerate(zip(peak_times[:20], peak_strengths[:20])):
        print(f"  {int(t*1000):6d}ms - strength: {s:.2f}")
    
    return beat_data

if __name__ == '__main__':
    music_file = 'Nutcracker/wwwroot/music/trans-siberian-orchestra-wizards-in-winter.mp3'
    analyze_audio(music_file)
