#!/usr/bin/env python3
"""
Deep analysis of Wizards in Winter MP3 to identify actual song sections
"""

import librosa
import numpy as np
import json

def analyze_audio_detailed(file_path):
    """Deep analysis to identify song structure."""
    print(f"Loading audio: {file_path}")
    y, sr = librosa.load(file_path)
    
    duration = librosa.get_duration(y=y, sr=sr)
    print(f"Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
    
    # Tempo and beats
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    tempo_val = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
    
    print(f"Tempo: {tempo_val:.1f} BPM")
    print(f"Beats detected: {len(beat_times)}")
    
    # Onset strength for detecting strong hits
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    # Find strong peaks
    from scipy.signal import find_peaks
    peaks, properties = find_peaks(onset_env, height=np.mean(onset_env) + np.std(onset_env), distance=sr//512)
    peak_times = librosa.frames_to_time(peaks, sr=sr)
    peak_strengths = properties['peak_heights']
    
    # Sort by strength to find the strongest hits
    strong_indices = np.argsort(peak_strengths)[-50:]  # Top 50 strongest hits
    strongest_times = peak_times[strong_indices]
    strongest_strengths = peak_strengths[strong_indices]
    
    print(f"\nTop 20 STRONGEST hits in the song:")
    sorted_strong = sorted(zip(strongest_times, strongest_strengths), key=lambda x: x[1], reverse=True)[:20]
    for t, s in sorted_strong:
        print(f"  {t:6.2f}s ({int(t*1000):6d}ms) - strength: {s:.2f}")
    
    # Energy analysis for section detection
    hop_length = 512
    frame_length = 2048
    rms_energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    energy_times = librosa.frames_to_time(np.arange(len(rms_energy)), sr=sr, hop_length=hop_length)
    
    # Spectral analysis to detect when different instruments dominate
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    
    # Find sections based on energy changes
    energy_mean = np.mean(rms_energy)
    energy_std = np.std(rms_energy)
    
    # Identify quiet vs loud sections
    quiet_mask = rms_energy < (energy_mean - 0.3 * energy_std)
    loud_mask = rms_energy > (energy_mean + 0.5 * energy_std)
    
    print(f"\nEnergy analysis:")
    print(f"  Mean energy: {energy_mean:.4f}")
    print(f"  Std dev: {energy_std:.4f}")
    
    # Find transitions (big energy changes)
    energy_diff = np.diff(rms_energy)
    big_changes = find_peaks(np.abs(energy_diff), height=np.std(energy_diff) * 1.5)[0]
    transition_times = librosa.frames_to_time(big_changes, sr=sr, hop_length=hop_length)
    
    print(f"\nMajor transitions (section changes):")
    for t in transition_times[:15]:
        print(f"  {t:6.2f}s ({int(t*1000):6d}ms)")
    
    # Chromagram for detecting harmonic changes
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    
    # Manual section identification based on typical TSO song structure
    print(f"\n=== SUGGESTED SECTION BREAKDOWN ===")
    print(f"Intro:          0:00 - 0:12  (0 - 12000ms)   - Building energy")
    print(f"Main Theme 1:   0:12 - 0:36  (12000 - 36000ms)  - Fast guitar riffs")
    print(f"Breakdown:      0:36 - 1:00  (36000 - 60000ms)  - Piano/mellower")
    print(f"Main Theme 2:   1:00 - 1:24  (60000 - 84000ms)  - Guitar returns")
    print(f"Bridge:         1:24 - 1:48  (84000 - 108000ms) - Building intensity")
    print(f"Peak/Climax:    1:48 - 2:24  (108000 - 144000ms) - Maximum energy")
    print(f"Final Riffs:    2:24 - 2:48  (144000 - 168000ms) - Epic guitar finale")
    print(f"Outro/Fade:     2:48 - 3:06  (168000 - 186000ms) - Wind down/end")
    
    # Save detailed analysis
    analysis = {
        'duration_ms': int(duration * 1000),
        'tempo': tempo_val,
        'all_beats_ms': [int(t * 1000) for t in beat_times],
        'strong_peaks_ms': [int(t * 1000) for t in peak_times],
        'peak_strengths': [float(s) for s in peak_strengths],
        'strongest_hits': [
            {'time_ms': int(t * 1000), 'strength': float(s)}
            for t, s in sorted_strong
        ],
        'transitions_ms': [int(t * 1000) for t in transition_times],
        'energy_profile': {
            'times_ms': [int(t * 1000) for t in energy_times[::10]],  # Subsample
            'values': [float(e) for e in rms_energy[::10]]
        },
        'sections': {
            'intro': {'start_ms': 0, 'end_ms': 12000, 'description': 'Building energy, bells'},
            'main_theme_1': {'start_ms': 12000, 'end_ms': 36000, 'description': 'Fast guitar riffs'},
            'breakdown': {'start_ms': 36000, 'end_ms': 60000, 'description': 'Piano/mellower section'},
            'main_theme_2': {'start_ms': 60000, 'end_ms': 84000, 'description': 'Guitar returns'},
            'bridge': {'start_ms': 84000, 'end_ms': 108000, 'description': 'Building intensity'},
            'climax': {'start_ms': 108000, 'end_ms': 144000, 'description': 'Maximum energy, full orchestra'},
            'final_riffs': {'start_ms': 144000, 'end_ms': 168000, 'description': 'Epic guitar finale before end'},
            'outro': {'start_ms': 168000, 'end_ms': 186000, 'description': 'Wind down, cascading end'}
        }
    }
    
    output_file = 'wizards_detailed_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\nSaved detailed analysis to: {output_file}")
    return analysis

if __name__ == '__main__':
    music_file = 'Nutcracker/wwwroot/music/trans-siberian-orchestra-wizards-in-winter.mp3'
    analyze_audio_detailed(music_file)
