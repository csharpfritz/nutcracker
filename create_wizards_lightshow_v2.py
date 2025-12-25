#!/usr/bin/env python3
"""
Generate the Wizards in Winter lightshow JSON - IMPROVED VERSION
- Bold, readable text
- Persistent snowflakes that stay visible
- Beat-synced to actual audio analysis
"""

import json
from typing import List, Tuple

# LED Matrix configuration
WIDTH = 32
HEIGHT = 8
TOTAL_LEDS = 256

def xy_to_led(x: int, y: int) -> int:
    """Convert matrix coordinates to LED index for serpentine wiring."""
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return -1
    if x % 2 == 0:  # Even columns go DOWN (0→7)
        return x * HEIGHT + y
    else:           # Odd columns go UP (7→0)
        return x * HEIGHT + (HEIGHT - 1 - y)

def get_column_leds(x: int) -> List[int]:
    """Get all LED indices for a column."""
    return [xy_to_led(x, y) for y in range(HEIGHT) if xy_to_led(x, y) >= 0]

def get_row_leds(y: int) -> List[int]:
    """Get all LED indices for a row."""
    return [xy_to_led(x, y) for x in range(WIDTH) if xy_to_led(x, y) >= 0]

# Winter magic color palette
COLORS = {
    'ice_blue': '#0099FF',
    'deep_blue': '#0066CC',
    'dark_blue': '#003366',
    'purple': '#9900CC',
    'deep_purple': '#6600CC',
    'magenta': '#CC00CC',
    'bright_magenta': '#FF00CC',
    'white': '#CCCCCC',
    'bright_white': '#FFFFFF',
    'cyan': '#00CCCC',
    'dim_blue': '#002244',
    'black': '#000000'
}

class LightshowGenerator:
    def __init__(self, beat_data):
        self.frames = []
        self.current_time = 0
        self.beat_data = beat_data
        self.beats = beat_data['beat_times_ms']
        self.strong_beats = beat_data['strong_beats_ms']
        
    def add_frame(self, effect: str, timestamp_ms: int = None, **kwargs):
        """Add a frame to the lightshow."""
        if timestamp_ms is not None:
            self.current_time = timestamp_ms
        
        frame = {
            'timestampMs': self.current_time,
            'effect': effect
        }
        frame.update(kwargs)
        self.frames.append(frame)
    
    def advance_time(self, ms: int):
        """Advance the current timestamp."""
        self.current_time += ms
    
    # ============ SNOWFLAKE PATTERNS ============
    
    def get_snowflake_6point(self, center_x: int, center_y: int) -> List[int]:
        """
        Create an intricate 6-point snowflake pattern.
        Size: approximately 7x7 pixels
        """
        offsets = [
            # Center (make it brighter/more visible)
            (0, 0),
            # Main 6 arms (vertical and diagonals)
            (0, -1), (0, -2), (0, -3),  # Top arm
            (0, 1), (0, 2), (0, 3),      # Bottom arm
            (-1, -1), (-2, -2),          # Top-left diagonal
            (1, -1), (2, -2),            # Top-right diagonal
            (-1, 1), (-2, 2),            # Bottom-left diagonal
            (1, 1), (2, 2),              # Bottom-right diagonal
            # Branch tips (make it intricate)
            (-1, -2), (1, -2),           # Top arm branches
            (-1, 2), (1, 2),             # Bottom arm branches
            (-2, -1), (-2, 0), (-2, 1),  # Left arm
            (2, -1), (2, 0), (2, 1),     # Right arm
            # Extra detail points
            (-1, 0), (1, 0),             # Horizontal extensions
        ]
        
        leds = []
        for dx, dy in offsets:
            led = xy_to_led(center_x + dx, center_y + dy)
            if led >= 0:
                leds.append(led)
        return list(set(leds))  # Remove duplicates
    
    def add_persistent_snowflake(self, start_x: int, color: str, start_time: int, stay_duration: int):
        """
        Animate a snowflake that STAYS VISIBLE for a long time.
        Falls slowly, then stays in place for the duration before fading.
        """
        # Fall phase (quick, 1 second)
        fall_duration = 1000
        steps = HEIGHT - 2  # Fall from y=1 to y=6 (leave room at bottom)
        step_time = fall_duration // steps
        
        # Falling animation
        for step in range(steps + 1):
            y = step + 1  # Start at y=1
            if y < HEIGHT - 1:
                leds = self.get_snowflake_6point(start_x, y)
                self.add_frame('set', start_time + step * step_time, color=color, leds=leds)
                
                # Dim previous position slightly (not completely remove)
                if step > 0:
                    prev_leds = self.get_snowflake_6point(start_x, step)
                    self.add_frame('set', start_time + step * step_time + 30, 
                                 color=COLORS['dim_blue'], leds=prev_leds)
        
        # STAY phase - snowflake remains visible
        final_y = min(steps + 1, HEIGHT - 2)
        final_leds = self.get_snowflake_6point(start_x, final_y)
        
        # Keep it bright and visible
        stay_start = start_time + fall_duration
        self.add_frame('set', stay_start, color=color, leds=final_leds)
        self.add_frame('set', stay_start + stay_duration // 2, color=color, leds=final_leds)
        
        # Gentle fade out at the end (gradual, not instant)
        fade_start = stay_start + stay_duration
        self.add_frame('set', fade_start, color=COLORS['ice_blue'], leds=final_leds)
        self.add_frame('set', fade_start + 300, color=COLORS['deep_blue'], leds=final_leds)
        self.add_frame('set', fade_start + 600, color=COLORS['dim_blue'], leds=final_leds)
    
    # ============ STEPPING ANIMATIONS (Piano Solos) ============
    
    def add_stepping_animation(self, start_time: int, duration: int, direction: str = 'up'):
        """
        Create stepping/staircase animation - perfect for piano solos.
        Pixels light up in a cascading staircase pattern.
        """
        step_time = 80  # Time per step in ms
        steps = duration // step_time
        
        for step in range(steps):
            timestamp = start_time + step * step_time
            
            # Create diagonal stepping pattern
            leds = []
            for offset in range(5):  # 5 diagonals visible at once
                if direction == 'up':
                    y = (step + offset) % HEIGHT
                    x = ((step + offset) * 2) % WIDTH
                else:  # down
                    y = HEIGHT - 1 - ((step + offset) % HEIGHT)
                    x = ((step + offset) * 2) % WIDTH
                
                # Light up 2-3 columns for each step
                for dx in range(3):
                    if x + dx < WIDTH:
                        led = xy_to_led(x + dx, y)
                        if led >= 0:
                            leds.append(led)
            
            # Alternate colors for visual interest
            colors = [COLORS['ice_blue'], COLORS['cyan'], COLORS['white'], COLORS['magenta']]
            color = colors[(step // 4) % len(colors)]
            
            if leds:
                self.add_frame('set', timestamp, color=color, leds=leds)
    
    def add_piano_cascade(self, start_time: int, duration: int):
        """Piano keys cascading down - elegant falling pattern."""
        cascade_time = 60  # ms between cascades
        cascades = duration // cascade_time
        
        for cascade in range(cascades):
            timestamp = start_time + cascade * cascade_time
            
            # Each cascade is a vertical column of pixels falling
            x = (cascade * 3) % WIDTH
            
            for y in range(HEIGHT):
                leds = []
                # Light 2 columns together
                for dx in range(2):
                    if x + dx < WIDTH:
                        led = xy_to_led(x + dx, y)
                        if led >= 0:
                            leds.append(led)
                
                # Color gradient from top to bottom
                colors = [COLORS['white'], COLORS['cyan'], COLORS['ice_blue'], COLORS['deep_blue']]
                color = colors[y // 2] if y // 2 < len(colors) else COLORS['dim_blue']
                
                if leds:
                    self.add_frame('set', timestamp + y * 30, color=color, leds=leds)
    
    # ============ ROCKING WIPES (Guitar Riffs) ============
    
    def add_rocking_wipe(self, start_time: int, duration: int, intensity: str = 'medium'):
        """
        Rocking side-to-side wipe for guitar riffs.
        Creates a back-and-forth sweeping motion with energy.
        """
        if intensity == 'high':
            wipe_time = 150  # Fast rocking
            colors = [COLORS['bright_magenta'], COLORS['bright_white'], COLORS['cyan']]
        else:
            wipe_time = 200  # Medium rocking
            colors = [COLORS['magenta'], COLORS['purple'], COLORS['ice_blue']]
        
        wipes = duration // wipe_time
        
        for wipe in range(wipes):
            timestamp = start_time + wipe * wipe_time
            direction = 'right' if wipe % 2 == 0 else 'left'
            color = colors[wipe % len(colors)]
            
            if direction == 'right':
                # Sweep right with trailing effect
                sweep_duration = wipe_time // 2
                for x in range(WIDTH):
                    leds = get_column_leds(x)
                    frame_time = timestamp + (x * sweep_duration // WIDTH)
                    self.add_frame('set', frame_time, color=color, leds=leds)
            else:
                # Sweep left with trailing effect
                sweep_duration = wipe_time // 2
                for x in range(WIDTH - 1, -1, -1):
                    leds = get_column_leds(x)
                    frame_time = timestamp + ((WIDTH - 1 - x) * sweep_duration // WIDTH)
                    self.add_frame('set', frame_time, color=color, leds=leds)
    
    def add_guitar_burst(self, start_time: int, center_x: int = None):
        """Explosive burst pattern for guitar hits."""
        if center_x is None:
            center_x = WIDTH // 2
        
        center_y = HEIGHT // 2
        
        # Expand outward from center in waves
        for radius in range(1, 8):
            leds = []
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    dist = abs(x - center_x) + abs(y - center_y)
                    if dist == radius:
                        led = xy_to_led(x, y)
                        if led >= 0:
                            leds.append(led)
            
            # Color fades from bright to dim as it expands
            colors = [COLORS['bright_white'], COLORS['bright_magenta'], COLORS['magenta'], 
                     COLORS['purple'], COLORS['ice_blue'], COLORS['deep_blue'], COLORS['dim_blue']]
            color = colors[min(radius - 1, len(colors) - 1)]
            
            if leds:
                self.add_frame('set', start_time + radius * 40, color=color, leds=leds)
    
    # ============ BOLD TEXT DISPLAY ============
    
    def get_bold_5x7_char(self, char: str) -> List[Tuple[int, int]]:
        """Get BOLD 5x7 pixel font coordinates for a character."""
        # BOLD font - thicker strokes for better readability
        fonts = {
            'W': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,4),(1,5),(1,6),
                  (2,3),(2,4),(2,5),(2,6),
                  (3,4),(3,5),(3,6),
                  (4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
            'I': [(0,0),(1,0),(2,0),(3,0),
                  (1,1),(2,1),
                  (1,2),(2,2),
                  (1,3),(2,3),
                  (1,4),(2,4),
                  (1,5),(2,5),
                  (0,6),(1,6),(2,6),(3,6)],
            'Z': [(0,0),(1,0),(2,0),(3,0),(4,0),
                  (3,1),(4,1),
                  (2,2),(3,2),
                  (1,3),(2,3),
                  (0,4),(1,4),
                  (0,5),(0,6),(1,6),(2,6),(3,6),(4,6)],
            'A': [(1,0),(2,0),(3,0),
                  (0,1),(1,1),(3,1),(4,1),
                  (0,2),(4,2),
                  (0,3),(1,3),(2,3),(3,3),(4,3),
                  (0,4),(4,4),
                  (0,5),(4,5),
                  (0,6),(4,6)],
            'R': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,0),(2,0),(3,0),
                  (4,1),(4,2),
                  (1,3),(2,3),(3,3),
                  (2,4),(3,4),
                  (3,5),(4,5),
                  (3,6),(4,6)],
            'D': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,0),(2,0),(3,0),
                  (4,1),(4,2),(4,3),(4,4),(4,5),
                  (1,6),(2,6),(3,6)],
            'S': [(1,0),(2,0),(3,0),(4,0),
                  (0,1),(0,2),
                  (1,3),(2,3),(3,3),
                  (4,4),(4,5),
                  (0,6),(1,6),(2,6),(3,6)],
            'M': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,1),(1,2),
                  (2,2),(2,3),
                  (3,1),(3,2),
                  (4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
            'G': [(1,0),(2,0),(3,0),(4,0),
                  (0,1),(0,2),(0,3),(0,4),(0,5),
                  (2,3),(3,3),(4,3),
                  (4,4),(4,5),
                  (1,6),(2,6),(3,6)],
            'C': [(1,0),(2,0),(3,0),(4,0),
                  (0,1),(0,2),(0,3),(0,4),(0,5),
                  (1,6),(2,6),(3,6),(4,6)],
            'T': [(0,0),(1,0),(2,0),(3,0),(4,0),
                  (2,1),(2,2),(2,3),(2,4),(2,5),(2,6),
                  (1,1),(3,1)],
            'E': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,0),(2,0),(3,0),(4,0),
                  (1,3),(2,3),(3,3),
                  (1,6),(2,6),(3,6),(4,6)],
            'N': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,1),(1,2),
                  (2,2),(2,3),(2,4),
                  (3,4),(3,5),
                  (4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
        }
        return fonts.get(char.upper(), [])
    
    def display_text(self, text: str, start_x: int, start_y: int, color: str, timestamp: int):
        """Display bold text at specified position."""
        leds = []
        x_offset = 0
        
        for char in text:
            char_pixels = self.get_bold_5x7_char(char)
            for dx, dy in char_pixels:
                led = xy_to_led(start_x + x_offset + dx, start_y + dy)
                if led >= 0:
                    leds.append(led)
            x_offset += 6  # 5 pixels + 1 space
        
        if leds:
            self.add_frame('set', timestamp, color=color, leds=leds)
    
    def add_flashing_text(self, text: str, start_x: int, start_y: int, start_time: int, hold_time: int):
        """Display text with flash sequence, hold, and fade."""
        # Flash sequence (3 flashes with increasing intensity)
        self.display_text(text, start_x, start_y, COLORS['deep_purple'], start_time)
        self.display_text(text, start_x, start_y, COLORS['dim_blue'], start_time + 150)
        self.display_text(text, start_x, start_y, COLORS['magenta'], start_time + 300)
        self.display_text(text, start_x, start_y, COLORS['dim_blue'], start_time + 450)
        self.display_text(text, start_x, start_y, COLORS['bright_magenta'], start_time + 600)
        
        # Hold in bright white
        self.display_text(text, start_x, start_y, COLORS['bright_white'], start_time + 750)
        
        # Continue holding
        for i in range(hold_time // 500):
            self.display_text(text, start_x, start_y, COLORS['bright_white'], start_time + 750 + i * 500)
        
        # Fade out sequence
        fade_start = start_time + 750 + hold_time
        self.display_text(text, start_x, start_y, COLORS['white'], fade_start)
        self.display_text(text, start_x, start_y, COLORS['cyan'], fade_start + 200)
        self.display_text(text, start_x, start_y, COLORS['ice_blue'], fade_start + 400)
        self.display_text(text, start_x, start_y, COLORS['dim_blue'], fade_start + 600)
    
    # ============ COLUMN EFFECTS ============
    
    def add_column_sweep(self, start_x: int, end_x: int, color: str, start_time: int, duration: int):
        """Sweep columns from start to end."""
        step = 1 if end_x > start_x else -1
        columns = list(range(start_x, end_x + step, step))
        step_time = duration // len(columns)
        
        for i, x in enumerate(columns):
            leds = get_column_leds(x)
            self.add_frame('set', start_time + i * step_time, color=color, leds=leds)
    
    def add_ice_crystal_burst(self, corner: str, start_time: int):
        """Create ice crystal burst from corner."""
        corners = {
            'top_left': (0, 0),
            'top_right': (WIDTH-1, 0),
            'bottom_left': (0, HEIGHT-1),
            'bottom_right': (WIDTH-1, HEIGHT-1)
        }
        
        cx, cy = corners[corner]
        
        for radius in range(1, 6):
            leds = []
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) == radius:
                        led = xy_to_led(cx + dx, cy + dy)
                        if led >= 0:
                            leds.append(led)
            
            color = COLORS['bright_white'] if radius <= 2 else COLORS['ice_blue']
            self.add_frame('set', start_time + radius * 80, color=color, leds=leds)
    
    # ============ MAIN LIGHTSHOW GENERATOR ============
    
    def generate_wizards_in_winter(self):
        """Generate the complete Wizards in Winter lightshow - BEAT SYNCED."""
        duration_ms = self.beat_data['duration_ms']
        
        # Start with black screen
        self.add_frame('fill', 0, color=COLORS['black'])
        
        # Get beat ranges for different sections
        intro_beats = [b for b in self.strong_beats if 0 <= b < 15000]
        main1_beats = [b for b in self.strong_beats if 15000 <= b < 45000]
        breakdown_beats = [b for b in self.strong_beats if 45000 <= b < 75000]
        build_beats = [b for b in self.strong_beats if 75000 <= b < 105000]
        peak_beats = [b for b in self.strong_beats if 105000 <= b < 150000]
        finale_beats = [b for b in self.strong_beats if 150000 <= b < 170000]
        
        print(f"Beats per section:")
        print(f"  Intro: {len(intro_beats)} beats")
        print(f"  Main1: {len(main1_beats)} beats")
        print(f"  Breakdown: {len(breakdown_beats)} beats")
        print(f"  Build: {len(build_beats)} beats")
        print(f"  Peak: {len(peak_beats)} beats")
        print(f"  Finale: {len(finale_beats)} beats")
        
        # ===== INTRO (0:00 - 0:15) =====
        # Long-lasting snowflakes
        self.add_persistent_snowflake(16, COLORS['white'], 500, 10000)
        
        # Guitar bursts on strong beats
        for i, beat in enumerate(intro_beats[:4]):
            x = 8 + (i * 6) % 24
            self.add_guitar_burst(beat, x)
        
        # Column sweep
        if intro_beats:
            self.add_column_sweep(0, 15, COLORS['deep_purple'], intro_beats[2], 1500)
            self.add_column_sweep(31, 16, COLORS['magenta'], intro_beats[2], 1500)
        
        # More snowflakes
        self.add_persistent_snowflake(10, COLORS['cyan'], 8000, 12000)
        self.add_persistent_snowflake(24, COLORS['ice_blue'], 10000, 10000)
        
        # ===== MAIN THEME (0:15 - 0:45) =====
        # "WIZARDS" text
        self.add_flashing_text("WIZARDS", 2, 0, 15000, 2500)
        
        # Rocking wipes for guitar riffs (high energy)
        self.add_rocking_wipe(18000, 6000, 'high')
        
        # Column sweeps synced to beats
        for i in range(min(8, len(main1_beats))):
            beat = main1_beats[i]
            if i % 2 == 0:
                self.add_column_sweep(0, 31, COLORS['ice_blue'], beat, 600)
            else:
                self.add_column_sweep(31, 0, COLORS['purple'], beat, 600)
        
        # Guitar bursts on strong beats
        for i, beat in enumerate(main1_beats[::3]):  # Every 3rd beat
            x = 8 + (i * 8) % 24
            self.add_guitar_burst(beat, x)
        
        # Persistent snowflakes throughout
        self.add_persistent_snowflake(8, COLORS['white'], 20000, 15000)
        self.add_persistent_snowflake(16, COLORS['cyan'], 22000, 15000)
        self.add_persistent_snowflake(24, COLORS['ice_blue'], 24000, 13000)
        
        # More rocking wipes
        self.add_rocking_wipe(30000, 8000, 'medium')
        
        # Ice crystal bursts on major beats
        if len(main1_beats) >= 10:
            self.add_ice_crystal_burst('top_left', main1_beats[8])
            self.add_ice_crystal_burst('top_right', main1_beats[9])
        
        # ===== BREAKDOWN (0:45 - 1:15) - PIANO SOLO SECTION =====
        # "WINTER" text
        self.add_flashing_text("WINTER", 3, 0, 45000, 2500)
        
        # More visible snowflakes (longer duration)
        self.add_persistent_snowflake(6, COLORS['white'], 48000, 20000)
        self.add_persistent_snowflake(14, COLORS['cyan'], 50000, 18000)
        self.add_persistent_snowflake(22, COLORS['ice_blue'], 52000, 16000)
        self.add_persistent_snowflake(28, COLORS['white'], 54000, 14000)
        
        # PIANO SOLO - Stepping animations (elegant)
        self.add_stepping_animation(48000, 8000, 'up')
        self.add_piano_cascade(56000, 10000)
        self.add_stepping_animation(66000, 8000, 'down')
        
        # Column effects synced (gentler for piano section)
        for i in range(min(12, len(breakdown_beats))):
            beat = breakdown_beats[i]
            color = COLORS['purple'] if i % 2 == 0 else COLORS['ice_blue']
            if i % 2 == 0:
                self.add_column_sweep(0, 15, color, beat, 400)
            else:
                self.add_column_sweep(31, 16, color, beat, 400)
        
        # Ice bursts
        if len(breakdown_beats) >= 8:
            self.add_ice_crystal_burst('bottom_left', breakdown_beats[6])
            self.add_ice_crystal_burst('bottom_right', breakdown_beats[7])
        
        # ===== BUILD TO CLIMAX (1:15 - 1:45) - GUITAR RIFFS =====
        # "MAGIC" text
        self.add_flashing_text("MAGIC", 5, 0, 75000, 2000)
        
        # Many visible snowflakes
        for i in range(6):
            x = 5 + i * 4
            self.add_persistent_snowflake(x, COLORS['white'], 78000 + i * 2000, 15000)
        
        # GUITAR RIFFS - Intense rocking wipes
        self.add_rocking_wipe(78000, 10000, 'high')
        self.add_rocking_wipe(89000, 12000, 'high')
        
        # Guitar bursts on beats
        for i, beat in enumerate(build_beats):
            x = 5 + (i * 6) % 26
            if i % 2 == 0:
                self.add_guitar_burst(beat, x)
        
        # Fast column sweeps
        for i in range(min(15, len(build_beats))):
            beat = build_beats[i]
            if i % 2 == 0:
                self.add_column_sweep(0, 31, COLORS['bright_magenta'], beat, 400)
            else:
                self.add_column_sweep(31, 0, COLORS['cyan'], beat, 400)
        
        # All corners ice burst
        if len(build_beats) >= 12:
            self.add_ice_crystal_burst('top_left', build_beats[10])
            self.add_ice_crystal_burst('top_right', build_beats[10] + 200)
            self.add_ice_crystal_burst('bottom_left', build_beats[11])
            self.add_ice_crystal_burst('bottom_right', build_beats[11] + 200)
        
        # ===== PEAK ENERGY (1:45 - 2:30) - MASSIVE GUITAR SECTION =====
        # "WIZARDS" again!
        self.add_flashing_text("WIZARDS", 2, 0, 105000, 3000)
        
        # Maximum snowflakes - all stay visible
        for i in range(10):
            x = 3 + i * 2
            self.add_persistent_snowflake(x, COLORS['cyan'], 110000 + i * 1500, 25000)
        
        # MASSIVE ROCKING WIPES for peak guitar energy
        self.add_rocking_wipe(110000, 15000, 'high')
        self.add_rocking_wipe(126000, 15000, 'high')
        
        # Guitar bursts on every strong beat
        for i, beat in enumerate(peak_beats):
            x = 6 + (i * 5) % 25
            self.add_guitar_burst(beat, x)
        
        # Ultra fast columns
        for i in range(min(25, len(peak_beats))):
            beat = peak_beats[i]
            if i % 4 == 0:
                self.add_column_sweep(0, 31, COLORS['bright_magenta'], beat, 300)
            elif i % 4 == 1:
                self.add_column_sweep(31, 0, COLORS['bright_white'], beat, 300)
            elif i % 4 == 2:
                self.add_column_sweep(0, 15, COLORS['ice_blue'], beat, 200)
                self.add_column_sweep(31, 16, COLORS['magenta'], beat, 200)
            else:
                self.add_column_sweep(15, 0, COLORS['purple'], beat, 200)
                self.add_column_sweep(16, 31, COLORS['cyan'], beat, 200)
        
        # "WINTER" text again
        self.add_flashing_text("WINTER", 3, 0, 128000, 2500)
        
        # Continuous ice bursts
        for i in range(min(8, len(peak_beats[20:]))):
            beat = peak_beats[20 + i]
            corners = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
            self.add_ice_crystal_burst(corners[i % 4], beat)
        
        # ===== PRE-FINALE (2:30 - 2:50) - FINAL GUITAR RIFFS =====
        # Rapid everything on beats
        self.add_rocking_wipe(150000, 18000, 'high')
        
        for i, beat in enumerate(finale_beats):
            # Guitar bursts on every beat
            self.add_guitar_burst(beat, 10 + (i % 3) * 6)
            
            # Fast column sweeps
            self.add_column_sweep(0, 31, COLORS['bright_magenta'], beat, 250)
            self.add_column_sweep(31, 0, COLORS['cyan'], beat + 250, 250)
        
        # Final visible snowflakes
        for i in range(8):
            x = 4 + i * 3
            self.add_persistent_snowflake(x, COLORS['white'], 155000 + i * 1000, 10000)
        
        # ===== FINALE (2:50 - 3:05) =====
        # Fade to dark blue
        self.add_frame('fill', 170000, color=COLORS['dark_blue'])
        self.add_frame('fill', 171000, color=COLORS['dim_blue'])
        
        # White pixel blizzard falling from top (multiple waves)
        for wave in range(10):
            wave_time = 172000 + wave * 200
            top_leds = get_row_leds(0)
            self.add_frame('set', wave_time, color=COLORS['bright_white'], leds=top_leds)
            
            for y in range(1, HEIGHT):
                row_leds = get_row_leds(y)
                self.add_frame('set', wave_time + y * 150, color=COLORS['bright_white'], leds=row_leds)
                
                prev_leds = get_row_leds(y - 1)
                fade_color = COLORS['white'] if y == 1 else COLORS['ice_blue']
                self.add_frame('set', wave_time + y * 150 + 50, color=fade_color, leds=prev_leds)
        
        # Clear for text scroll
        self.add_frame('fill', 177000, color=COLORS['dim_blue'])
        
        # Scroll "Wizards in Winter"
        full_text = "WIZARDS IN WINTER"
        scroll_duration = 7500
        text_width = len(full_text) * 6
        frames_count = text_width + WIDTH
        
        for frame in range(frames_count):
            x_pos = WIDTH - frame
            timestamp = 177500 + frame * (scroll_duration // frames_count)
            self.display_text(full_text, x_pos, 0, COLORS['bright_white'], timestamp)
            
            if frame > 0:
                self.display_text(full_text, x_pos + 1, 0, COLORS['ice_blue'], timestamp + 20)
        
        # Final fade
        self.add_frame('fill', 185000, color=COLORS['dim_blue'])
        self.add_frame('fill', duration_ms, color=COLORS['black'])
        
        # Sort frames by timestamp
        self.frames.sort(key=lambda f: f['timestampMs'])
        
        return {
            'name': 'Wizards in Winter',
            'description': 'Epic winter wizard themed lightshow with BOLD text, PERSISTENT snowflakes, and BEAT-SYNCED animations',
            'durationMs': duration_ms,
            'frames': self.frames
        }

def main():
    print("Loading beat data...")
    with open('wizards_beat_data.json', 'r') as f:
        beat_data = json.load(f)
    
    print(f"Generating IMPROVED Wizards in Winter lightshow...")
    print(f"  Duration: {beat_data['duration_ms']/1000:.1f}s")
    print(f"  Tempo: {beat_data['tempo']:.1f} BPM")
    print(f"  Beats: {len(beat_data['beat_times_ms'])}")
    print(f"  Strong beats: {len(beat_data['strong_beats_ms'])}")
    
    generator = LightshowGenerator(beat_data)
    lightshow = generator.generate_wizards_in_winter()
    
    output_path = 'Nutcracker/wwwroot/lights/wizards-in-winter.json'
    with open(output_path, 'w') as f:
        json.dump(lightshow, f, indent=2)
    
    print(f"\nGenerated: {output_path}")
    print(f"  Duration: {lightshow['durationMs']}ms ({lightshow['durationMs']//60000}:{(lightshow['durationMs']//1000)%60:02d})")
    print(f"  Total Frames: {len(lightshow['frames'])}")
    print(f"  Animation: {lightshow['description']}")
    print(f"\nIMPROVEMENTS:")
    print(f"  - BOLD text (thicker, more readable)")
    print(f"  - PERSISTENT snowflakes (stay visible 10-25 seconds)")
    print(f"  - BEAT-SYNCED timing (aligned to actual MP3)")
    print(f"  - STEPPING ANIMATIONS for piano solos (elegant cascades)")
    print(f"  - ROCKING WIPES for guitar riffs (side-to-side energy)")
    print(f"  - GUITAR BURSTS instead of lightning")
    print(f"\nEPIC LIGHTSHOW READY!")

if __name__ == '__main__':
    main()
