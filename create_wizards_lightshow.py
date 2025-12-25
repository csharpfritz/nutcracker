#!/usr/bin/env python3
"""
Generate the Wizards in Winter lightshow JSON
Trans-Siberian Orchestra - Epic winter wizard themed animation
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
    def __init__(self):
        self.frames = []
        self.current_time = 0
        
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
            # Center
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
    
    def add_falling_snowflake(self, start_x: int, color: str, start_time: int, fall_duration: int):
        """Animate a snowflake falling from top to bottom."""
        steps = HEIGHT - 1  # Fall from y=0 to y=7
        step_time = fall_duration // steps
        
        for step in range(steps + 1):
            y = step
            if y < HEIGHT:
                leds = self.get_snowflake_6point(start_x, y)
                self.add_frame('set', start_time + step * step_time, color=color, leds=leds)
                
                # Clear previous position (fade to dark blue instead of black)
                if step > 0:
                    prev_leds = self.get_snowflake_6point(start_x, step - 1)
                    self.add_frame('set', start_time + step * step_time + 20, 
                                 color=COLORS['dim_blue'], leds=prev_leds)
    
    # ============ LIGHTNING EFFECTS ============
    
    def get_lightning_bolt(self, x: int) -> List[Tuple[int, List[int]]]:
        """
        Create a jagged lightning bolt pattern down a column.
        Returns list of (y_position, led_indices) for animation frames.
        """
        bolt_frames = []
        y = 0
        current_x = x
        
        while y < HEIGHT:
            # Main bolt segment
            leds = [xy_to_led(current_x, y)]
            
            # Add width/branches
            if current_x > 0:
                leds.append(xy_to_led(current_x - 1, y))
            if current_x < WIDTH - 1:
                leds.append(xy_to_led(current_x + 1, y))
            
            # Filter valid LEDs
            leds = [led for led in leds if led >= 0]
            bolt_frames.append((y, leds))
            
            # Zigzag pattern
            y += 1
            if y < HEIGHT:
                if current_x > 2 and (y % 3 == 0):
                    current_x -= 1
                elif current_x < WIDTH - 3 and (y % 3 == 1):
                    current_x += 1
        
        return bolt_frames
    
    def add_quick_lightning_strike(self, x: int, start_time: int):
        """Quick lightning strike (2-3 frames, ~100ms total)."""
        bolt = self.get_lightning_bolt(x)
        all_leds = []
        for _, leds in bolt:
            all_leds.extend(leds)
        
        # Flash bright white
        self.add_frame('set', start_time, color=COLORS['bright_white'], leds=all_leds)
        self.add_frame('set', start_time + 30, color=COLORS['cyan'], leds=all_leds)
        self.add_frame('set', start_time + 60, color=COLORS['dim_blue'], leds=all_leds)
    
    def add_sustained_lightning(self, x: int, start_time: int, duration: int):
        """Sustained crackling lightning bolt."""
        bolt = self.get_lightning_bolt(x)
        all_leds = []
        for _, leds in bolt:
            all_leds.extend(leds)
        
        # Animate bolt growing from top to bottom
        for i, (y, leds) in enumerate(bolt):
            self.add_frame('set', start_time + i * 30, color=COLORS['bright_white'], leds=leds)
        
        # Hold and crackle
        flickers = duration // 100
        for flicker in range(flickers):
            color = COLORS['bright_white'] if flicker % 2 == 0 else COLORS['cyan']
            self.add_frame('set', start_time + 200 + flicker * 100, color=color, leds=all_leds)
        
        # Fade out
        self.add_frame('set', start_time + duration - 50, color=COLORS['ice_blue'], leds=all_leds)
        self.add_frame('set', start_time + duration, color=COLORS['dim_blue'], leds=all_leds)
    
    # ============ TEXT DISPLAY ============
    
    def get_5x7_char(self, char: str) -> List[Tuple[int, int]]:
        """Get 5x7 pixel font coordinates for a character (relative to origin)."""
        # Simplified 5x7 font (uppercase only)
        fonts = {
            'W': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,5),(1,6),
                  (2,4),(2,5),
                  (3,5),(3,6),
                  (4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
            'I': [(0,0),(1,0),(2,0),
                  (1,1),(1,2),(1,3),(1,4),(1,5),
                  (0,6),(1,6),(2,6)],
            'Z': [(0,0),(1,0),(2,0),(3,0),(4,0),
                  (3,1),(2,2),(1,3),(0,4),
                  (0,5),(0,6),(1,6),(2,6),(3,6),(4,6)],
            'A': [(1,0),(2,0),
                  (0,1),(3,1),
                  (0,2),(3,2),
                  (0,3),(1,3),(2,3),(3,3),
                  (0,4),(3,4),
                  (0,5),(3,5),
                  (0,6),(3,6)],
            'R': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,0),(2,0),(3,0),
                  (3,1),(3,2),
                  (1,3),(2,3),
                  (2,4),(3,5),(3,6)],
            'D': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,0),(2,0),
                  (3,1),(3,2),(3,3),(3,4),(3,5),
                  (1,6),(2,6)],
            'S': [(1,0),(2,0),(3,0),
                  (0,1),(0,2),
                  (1,3),(2,3),
                  (3,4),(3,5),
                  (0,6),(1,6),(2,6)],
            'M': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,1),
                  (2,2),
                  (3,1),
                  (4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
            'G': [(1,0),(2,0),(3,0),
                  (0,1),(0,2),(0,3),(0,4),(0,5),
                  (2,3),(3,3),(3,4),(3,5),
                  (1,6),(2,6),(3,6)],
            'C': [(1,0),(2,0),(3,0),
                  (0,1),(0,2),(0,3),(0,4),(0,5),
                  (1,6),(2,6),(3,6)],
            'T': [(0,0),(1,0),(2,0),(3,0),(4,0),
                  (2,1),(2,2),(2,3),(2,4),(2,5),(2,6)],
            'E': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,0),(2,0),(3,0),
                  (1,3),(2,3),
                  (1,6),(2,6),(3,6)],
            'N': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),
                  (1,1),
                  (2,2),(2,3),
                  (3,4),(3,5),
                  (4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
        }
        return fonts.get(char.upper(), [])
    
    def display_text(self, text: str, start_x: int, start_y: int, color: str, timestamp: int):
        """Display text at specified position."""
        leds = []
        x_offset = 0
        
        for char in text:
            char_pixels = self.get_5x7_char(char)
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
        self.display_text(text, start_x, start_y, COLORS['dim_blue'], start_time + 100)
        self.display_text(text, start_x, start_y, COLORS['magenta'], start_time + 200)
        self.display_text(text, start_x, start_y, COLORS['dim_blue'], start_time + 300)
        self.display_text(text, start_x, start_y, COLORS['bright_magenta'], start_time + 400)
        
        # Hold in bright white
        self.display_text(text, start_x, start_y, COLORS['bright_white'], start_time + 500)
        
        # Fade out sequence
        fade_start = start_time + 500 + hold_time
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
        # Define corner starting points
        corners = {
            'top_left': (0, 0),
            'top_right': (WIDTH-1, 0),
            'bottom_left': (0, HEIGHT-1),
            'bottom_right': (WIDTH-1, HEIGHT-1)
        }
        
        cx, cy = corners[corner]
        
        # Expand outward in waves
        for radius in range(1, 6):
            leds = []
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) + abs(dy) == radius:  # Diamond pattern
                        led = xy_to_led(cx + dx, cy + dy)
                        if led >= 0:
                            leds.append(led)
            
            color = COLORS['bright_white'] if radius <= 2 else COLORS['ice_blue']
            self.add_frame('set', start_time + radius * 80, color=color, leds=leds)
    
    # ============ MAIN LIGHTSHOW GENERATOR ============
    
    def generate_wizards_in_winter(self):
        """Generate the complete Wizards in Winter lightshow."""
        # Song duration: 3:05 = 185 seconds = 185000ms
        duration_ms = 185000
        
        # Start with black screen
        self.add_frame('fill', 0, color=COLORS['black'])
        
        # ===== INTRO (0:00 - 0:15) - 15000ms =====
        # Single snowflake falling, building energy
        self.add_falling_snowflake(16, COLORS['white'], 500, 2000)
        self.add_quick_lightning_strike(8, 2500)
        self.add_falling_snowflake(24, COLORS['cyan'], 3000, 2000)
        self.add_quick_lightning_strike(20, 5000)
        
        # Column sweep building
        self.add_column_sweep(0, 15, COLORS['deep_purple'], 6000, 1500)
        self.add_column_sweep(31, 16, COLORS['magenta'], 6000, 1500)
        
        # Ice crystal bursts from corners
        self.add_ice_crystal_burst('top_left', 8000)
        self.add_ice_crystal_burst('top_right', 8500)
        
        # More snowflakes
        self.add_falling_snowflake(10, COLORS['ice_blue'], 10000, 2000)
        self.add_falling_snowflake(22, COLORS['white'], 11000, 2000)
        
        self.add_sustained_lightning(5, 13000, 1500)
        
        # ===== MAIN THEME SECTION 1 (0:15 - 0:45) - Fast energy =====
        # "WIZARDS" text display
        self.add_flashing_text("WIZARDS", 2, 0, 15000, 2000)
        
        # Rapid column sweeps (intense!)
        for i in range(5):
            start = 18000 + i * 1200
            self.add_column_sweep(0, 31, COLORS['ice_blue'], start, 600)
            self.add_column_sweep(31, 0, COLORS['purple'], start + 600, 600)
        
        # Lightning strikes mixed in
        self.add_quick_lightning_strike(10, 19000)
        self.add_quick_lightning_strike(22, 20500)
        self.add_sustained_lightning(16, 22000, 1000)
        
        # Multiple snowflakes falling
        self.add_falling_snowflake(8, COLORS['white'], 24000, 1800)
        self.add_falling_snowflake(16, COLORS['cyan'], 24500, 1800)
        self.add_falling_snowflake(24, COLORS['ice_blue'], 25000, 1800)
        
        # More column action
        for i in range(4):
            start = 27000 + i * 1500
            self.add_column_sweep(0, 15, COLORS['magenta'], start, 700)
            self.add_column_sweep(31, 16, COLORS['purple'], start, 700)
            self.add_quick_lightning_strike(8 + i * 6, start + 800)
        
        # Ice crystals
        self.add_ice_crystal_burst('bottom_left', 30000)
        self.add_ice_crystal_burst('bottom_right', 30500)
        
        # ===== BREAKDOWN SECTION (0:45 - 1:15) - Still intense but more magical =====
        # "WINTER" text
        self.add_flashing_text("WINTER", 3, 0, 45000, 2000)
        
        # More snowflakes (3-4 at once)
        self.add_falling_snowflake(6, COLORS['white'], 48000, 2500)
        self.add_falling_snowflake(14, COLORS['cyan'], 48300, 2500)
        self.add_falling_snowflake(22, COLORS['ice_blue'], 48600, 2500)
        self.add_falling_snowflake(28, COLORS['white'], 48900, 2500)
        
        # Sustained lightning
        self.add_sustained_lightning(10, 51000, 1500)
        self.add_sustained_lightning(20, 52000, 1500)
        
        # Alternating columns (creates ripple effect)
        for i in range(16):
            time = 54000 + i * 150
            even_cols = [get_column_leds(x) for x in range(0, WIDTH, 2)]
            odd_cols = [get_column_leds(x) for x in range(1, WIDTH, 2)]
            
            color = COLORS['purple'] if i % 2 == 0 else COLORS['ice_blue']
            cols = even_cols if i % 2 == 0 else odd_cols
            
            all_leds = []
            for col in cols:
                all_leds.extend(col)
            self.add_frame('set', time, color=color, leds=all_leds)
        
        # More snowflakes
        self.add_falling_snowflake(4, COLORS['cyan'], 57000, 2000)
        self.add_falling_snowflake(12, COLORS['white'], 57500, 2000)
        self.add_falling_snowflake(20, COLORS['ice_blue'], 58000, 2000)
        self.add_falling_snowflake(26, COLORS['white'], 58500, 2000)
        
        # Quick lightning strikes
        self.add_quick_lightning_strike(8, 60000)
        self.add_quick_lightning_strike(16, 60500)
        self.add_quick_lightning_strike(24, 61000)
        
        # Vortex effect (spiral columns)
        spiral_order = [15, 16, 14, 17, 13, 18, 12, 19, 11, 20, 10, 21, 9, 22, 8, 23]
        for i, x in enumerate(spiral_order):
            self.add_frame('set', 62000 + i * 100, color=COLORS['magenta'], leds=get_column_leds(x))
        
        # Ice crystal bursts
        self.add_ice_crystal_burst('top_left', 65000)
        self.add_ice_crystal_burst('bottom_right', 65500)
        
        # More snowflakes
        self.add_falling_snowflake(10, COLORS['white'], 67000, 2000)
        self.add_falling_snowflake(22, COLORS['cyan'], 67500, 2000)
        
        # ===== BUILD TO CLIMAX (1:15 - 1:45) =====
        # "MAGIC" text
        self.add_flashing_text("MAGIC", 5, 0, 75000, 2000)
        
        # Increasing intensity - faster sweeps
        for i in range(6):
            start = 78000 + i * 1000
            self.add_column_sweep(0, 31, COLORS['bright_magenta'], start, 500)
            self.add_column_sweep(31, 0, COLORS['cyan'], start + 500, 500)
        
        # Lightning storm building
        self.add_sustained_lightning(5, 79000, 1200)
        self.add_quick_lightning_strike(15, 80500)
        self.add_sustained_lightning(25, 82000, 1200)
        self.add_quick_lightning_strike(12, 83500)
        self.add_quick_lightning_strike(20, 84000)
        
        # Multiple snowflakes
        for i in range(5):
            x = 6 + i * 5
            self.add_falling_snowflake(x, COLORS['white'], 85000 + i * 400, 1800)
        
        # All corners ice burst
        self.add_ice_crystal_burst('top_left', 87000)
        self.add_ice_crystal_burst('top_right', 87200)
        self.add_ice_crystal_burst('bottom_left', 87400)
        self.add_ice_crystal_burst('bottom_right', 87600)
        
        # More rapid columns
        for i in range(8):
            start = 89000 + i * 700
            self.add_column_sweep(0, 31, COLORS['purple'], start, 350)
            self.add_column_sweep(31, 0, COLORS['ice_blue'], start + 350, 350)
        
        # ===== PEAK ENERGY (1:45 - 2:30) - EVERYTHING AT ONCE =====
        # "WIZARDS" again!
        self.add_flashing_text("WIZARDS", 2, 0, 105000, 2500)
        
        # Massive lightning storm
        self.add_sustained_lightning(8, 108000, 1500)
        self.add_sustained_lightning(16, 108300, 1500)
        self.add_sustained_lightning(24, 108600, 1500)
        
        # Ultra fast column sweeps
        for i in range(12):
            start = 110000 + i * 800
            self.add_column_sweep(0, 31, COLORS['bright_magenta'], start, 400)
            self.add_column_sweep(31, 0, COLORS['bright_white'], start + 400, 400)
        
        # Continuous snowflakes
        for i in range(8):
            x = 4 + i * 3
            self.add_falling_snowflake(x, COLORS['cyan'], 120000 + i * 500, 1500)
        
        # Lightning bursts
        for i in range(6):
            x = 5 + i * 4
            self.add_quick_lightning_strike(x, 124000 + i * 600)
        
        # "WINTER" text again
        self.add_flashing_text("WINTER", 3, 0, 128000, 2000)
        
        # More column madness
        for i in range(10):
            start = 131000 + i * 600
            self.add_column_sweep(0, 15, COLORS['ice_blue'], start, 300)
            self.add_column_sweep(31, 16, COLORS['magenta'], start, 300)
            self.add_column_sweep(15, 0, COLORS['purple'], start + 300, 300)
            self.add_column_sweep(16, 31, COLORS['cyan'], start + 300, 300)
        
        # All corners burst repeatedly
        for i in range(3):
            start = 138000 + i * 1000
            self.add_ice_crystal_burst('top_left', start)
            self.add_ice_crystal_burst('top_right', start + 200)
            self.add_ice_crystal_burst('bottom_left', start + 400)
            self.add_ice_crystal_burst('bottom_right', start + 600)
        
        # More snowflakes
        for i in range(6):
            x = 8 + i * 4
            self.add_falling_snowflake(x, COLORS['white'], 142000 + i * 400, 1600)
        
        # Lightning finale build
        self.add_sustained_lightning(6, 146000, 1000)
        self.add_sustained_lightning(16, 146500, 1000)
        self.add_sustained_lightning(26, 147000, 1000)
        
        # ===== PRE-FINALE (2:30 - 2:50) - Building to the end =====
        # Rapid everything
        for i in range(15):
            start = 150000 + i * 500
            if i % 3 == 0:
                self.add_quick_lightning_strike(10 + (i % 3) * 6, start)
            self.add_column_sweep(0, 31, COLORS['bright_magenta'], start, 250)
            self.add_column_sweep(31, 0, COLORS['cyan'], start + 250, 250)
        
        # Final snowflake cascade
        for i in range(10):
            x = 3 + i * 2
            self.add_falling_snowflake(x, COLORS['white'], 158000 + i * 300, 1200)
        
        # Final ice crystal bursts
        for i in range(4):
            corners = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
            self.add_ice_crystal_burst(corners[i], 163000 + i * 300)
        
        # ===== FINALE (2:50 - 3:05) - Dark blue → blizzard → scroll text =====
        # Fade to dark blue
        self.add_frame('fill', 170000, color=COLORS['dark_blue'])
        self.add_frame('fill', 170500, color=COLORS['dim_blue'])
        
        # White pixel blizzard falling from top
        # Create multiple waves of white pixels falling
        for wave in range(12):
            wave_time = 171000 + wave * 200
            # Top row starts white
            top_leds = get_row_leds(0)
            self.add_frame('set', wave_time, color=COLORS['bright_white'], leds=top_leds)
            
            # Each row falls down
            for y in range(1, HEIGHT):
                row_leds = get_row_leds(y)
                self.add_frame('set', wave_time + y * 150, color=COLORS['bright_white'], leds=row_leds)
                
                # Previous rows fade
                prev_leds = get_row_leds(y - 1)
                fade_color = COLORS['white'] if y == 1 else COLORS['ice_blue']
                self.add_frame('set', wave_time + y * 150 + 50, color=fade_color, leds=prev_leds)
        
        # Clear for text scroll
        self.add_frame('fill', 177000, color=COLORS['dim_blue'])
        
        # Scroll "Wizards in Winter" - move text from right to left
        full_text = "WIZARDS IN WINTER"
        scroll_duration = 7000  # 7 seconds to scroll
        text_width = len(full_text) * 6  # 6 pixels per char
        frames_count = text_width + WIDTH  # Move completely across screen
        
        for frame in range(frames_count):
            x_pos = WIDTH - frame
            timestamp = 177500 + frame * (scroll_duration // frames_count)
            
            # Display text at current position
            self.display_text(full_text, x_pos, 0, COLORS['bright_white'], timestamp)
            
            # Fade previous position to create smooth scroll
            if frame > 0:
                self.display_text(full_text, x_pos + 1, 0, COLORS['ice_blue'], timestamp + 20)
        
        # Final fade to dark blue
        self.add_frame('fill', 184500, color=COLORS['dim_blue'])
        self.add_frame('fill', duration_ms, color=COLORS['black'])
        
        # Sort frames by timestamp
        self.frames.sort(key=lambda f: f['timestampMs'])
        
        return {
            'name': 'Wizards in Winter',
            'description': 'Epic winter wizard themed lightshow with intricate snowflakes, lightning bolts, magical text, and intense energy throughout',
            'durationMs': duration_ms,
            'frames': self.frames
        }

def main():
    print("Generating Wizards in Winter lightshow...")
    generator = LightshowGenerator()
    lightshow = generator.generate_wizards_in_winter()
    
    output_path = 'Nutcracker/wwwroot/lights/wizards-in-winter.json'
    with open(output_path, 'w') as f:
        json.dump(lightshow, f, indent=2)
    
    print(f"\n✓ Generated: {output_path}")
    print(f"  Duration: {lightshow['durationMs']}ms ({lightshow['durationMs']//60000}:{(lightshow['durationMs']//1000)%60:02d})")
    print(f"  Total Frames: {len(lightshow['frames'])}")
    print(f"  Animation: {lightshow['description']}")
    print(f"  Colors: Ice Blue, Purple, Magenta, Cyan, White")
    print(f"\n🎆 EPIC LIGHTSHOW READY! ⚡❄️")

if __name__ == '__main__':
    main()
