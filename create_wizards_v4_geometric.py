#!/usr/bin/env python3
"""
Wizards in Winter - V4 GEOMETRIC PATTERNS
Focus on growing/twisting squares and geometric shapes
Remove rapid flashing columns
"""

import json
from typing import List

WIDTH = 32
HEIGHT = 8

def xy_to_led(x: int, y: int) -> int:
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return -1
    if x % 2 == 0:
        return x * HEIGHT + y
    else:
        return x * HEIGHT + (HEIGHT - 1 - y)

def get_column_leds(x: int) -> List[int]:
    return [xy_to_led(x, y) for y in range(HEIGHT) if xy_to_led(x, y) >= 0]

def get_row_leds(y: int) -> List[int]:
    return [xy_to_led(x, y) for x in range(WIDTH) if xy_to_led(x, y) >= 0]

COLORS = {
    'ice_blue': '#0099CC',
    'deep_blue': '#0066CC',
    'purple': '#9900CC',
    'magenta': '#CC00CC',
    'bright_magenta': '#FF00CC',
    'white': '#CCCCCC',
    'bright_white': '#FFFFFF',
    'cyan': '#00CCCC',
    'dim_blue': '#003366',
    'black': '#000000'
}

class LightshowGenerator:
    def __init__(self, beat_data):
        self.frames = []
        self.beat_data = beat_data
        
    def add_frame(self, timestamp_ms: int, effect: str, **kwargs):
        frame = {'timestampMs': timestamp_ms, 'effect': effect}
        frame.update(kwargs)
        self.frames.append(frame)
    
    def get_snowflake(self, cx: int, cy: int) -> List[int]:
        """6-point snowflake."""
        offsets = [
            (0,0), (0,-1), (0,-2), (0,-3), (0,1), (0,2), (0,3),
            (-1,-1), (-2,-2), (1,-1), (2,-2),
            (-1,1), (-2,2), (1,1), (2,2),
            (-1,-2), (1,-2), (-1,2), (1,2),
            (-2,-1), (-2,0), (-2,1), (2,-1), (2,0), (2,1),
            (-1,0), (1,0)
        ]
        leds = []
        for dx, dy in offsets:
            led = xy_to_led(cx + dx, cy + dy)
            if led >= 0:
                leds.append(led)
        return list(set(leds))
    
    def add_persistent_snowflake(self, x: int, color: str, start: int, duration: int):
        """Snowflake that falls and stays visible."""
        for step in range(6):
            y = step + 1
            if y < HEIGHT - 1:
                leds = self.get_snowflake(x, y)
                self.add_frame(start + step * 150, 'set', color=color, leds=leds)
                if step > 0:
                    prev = self.get_snowflake(x, step)
                    self.add_frame(start + step * 150 + 50, 'set', color=COLORS['dim_blue'], leds=prev)
        
        final_y = min(6, HEIGHT - 2)
        final_leds = self.get_snowflake(x, final_y)
        for t in range(0, duration, 3000):
            self.add_frame(start + 900 + t, 'set', color=color, leds=final_leds)
        
        self.add_frame(start + 900 + duration, 'set', color=COLORS['ice_blue'], leds=final_leds)
        self.add_frame(start + 900 + duration + 300, 'set', color=COLORS['dim_blue'], leds=final_leds)
    
    def add_expanding_square(self, t: int, center_x: int = 16, center_y: int = 3):
        """Expanding square from center - THIS IS WHAT THEY LOVE!"""
        for r in range(1, 12):
            leds = []
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    # Diamond/square pattern
                    if abs(x - center_x) + abs(y - center_y) == r:
                        led = xy_to_led(x, y)
                        if led >= 0:
                            leds.append(led)
            
            # Color progression from bright to dim
            if r <= 2:
                color = COLORS['bright_white']
            elif r <= 4:
                color = COLORS['bright_magenta']
            elif r <= 6:
                color = COLORS['magenta']
            elif r <= 8:
                color = COLORS['purple']
            else:
                color = COLORS['ice_blue']
            
            if leds:
                self.add_frame(t + r * 35, 'set', color=color, leds=leds)
    
    def add_rotating_square(self, start: int, duration: int, cx: int = 16):
        """Rotating square pattern that twists."""
        steps = duration // 80
        for step in range(steps):
            t = start + step * 80
            leds = []
            
            # Create rotating pattern
            angle_offset = step % 8
            for offset in range(8):
                angle = (offset + angle_offset) % 8
                # 8 positions around a diamond
                positions = [
                    (cx, 0), (cx+2, 1), (cx+3, 3), (cx+2, 5),
                    (cx, 7), (cx-2, 5), (cx-3, 3), (cx-2, 1)
                ]
                if angle < len(positions):
                    x, y = positions[angle]
                    # Add multiple pixels for thickness
                    for dx in [-1, 0, 1]:
                        led = xy_to_led(x + dx, y)
                        if led >= 0:
                            leds.append(led)
            
            color = [COLORS['magenta'], COLORS['cyan'], COLORS['purple']][step % 3]
            if leds:
                self.add_frame(t, 'set', color=color, leds=leds)
    
    def add_concentric_rings(self, start: int, cx: int = 16):
        """Concentric rings expanding then contracting."""
        # Expand
        for r in range(1, 10):
            leds = []
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    if abs(x - cx) + abs(y - 3) == r:
                        led = xy_to_led(x, y)
                        if led >= 0:
                            leds.append(led)
            colors = [COLORS['cyan'], COLORS['ice_blue'], COLORS['purple'], COLORS['magenta']]
            color = colors[r % len(colors)]
            if leds:
                self.add_frame(start + r * 40, 'set', color=color, leds=leds)
    
    def add_dual_expanding_squares(self, t: int):
        """Two squares expanding from different centers simultaneously."""
        for r in range(1, 8):
            leds1 = []
            leds2 = []
            
            # Left square
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    if abs(x - 8) + abs(y - 3) == r:
                        led = xy_to_led(x, y)
                        if led >= 0:
                            leds1.append(led)
            
            # Right square
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    if abs(x - 24) + abs(y - 3) == r:
                        led = xy_to_led(x, y)
                        if led >= 0:
                            leds2.append(led)
            
            colors = [COLORS['bright_white'], COLORS['cyan'], COLORS['magenta'], COLORS['purple']]
            color = colors[r % len(colors)]
            
            if leds1:
                self.add_frame(t + r * 40, 'set', color=color, leds=leds1)
            if leds2:
                self.add_frame(t + r * 40, 'set', color=color, leds=leds2)
    
    def add_wave_sweep(self, start: int, direction: str, color: str, speed: int = 50):
        """Smooth wave sweep."""
        if direction == 'right':
            for x in range(WIDTH):
                leds = get_column_leds(x)
                self.add_frame(start + x * speed, 'set', color=color, leds=leds)
        else:
            for x in range(WIDTH - 1, -1, -1):
                leds = get_column_leds(x)
                self.add_frame(start + (WIDTH - 1 - x) * speed, 'set', color=color, leds=leds)
    
    def add_text_short(self, text: str, x: int, start: int, hold: int):
        """Display short text that FITS on screen."""
        fonts = {
            'W': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,5),(2,4),(3,5),(4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
            'I': [(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6)],
            'Z': [(0,0),(1,0),(2,0),(3,0),(3,1),(2,2),(2,3),(1,4),(0,5),(0,6),(1,6),(2,6),(3,6)],
            'R': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,1),(1,3),(2,3),(2,4),(3,5),(3,6)],
            'D': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,1),(3,2),(3,3),(3,4),(3,5),(1,6),(2,6)],
            'S': [(1,0),(2,0),(3,0),(0,1),(0,2),(1,3),(2,3),(3,4),(3,5),(0,6),(1,6),(2,6)],
        }
        
        def display(color: str, t: int):
            leds = []
            x_off = 0
            for char in text:
                if char in fonts:
                    for dx, dy in fonts[char]:
                        led = xy_to_led(x + x_off + dx, dy)
                        if led >= 0:
                            leds.append(led)
                    x_off += 5  # Tighter spacing
            if leds:
                self.add_frame(t, 'set', color=color, leds=leds)
        
        # Flash in
        display(COLORS['magenta'], start)
        display(COLORS['dim_blue'], start + 100)
        display(COLORS['bright_magenta'], start + 200)
        display(COLORS['bright_white'], start + 300)
        
        # Hold
        for t in range(0, hold, 500):
            display(COLORS['bright_white'], start + 400 + t)
        
        # Fade
        display(COLORS['cyan'], start + 400 + hold)
        display(COLORS['ice_blue'], start + 400 + hold + 200)
        display(COLORS['dim_blue'], start + 400 + hold + 400)
    
    def generate(self):
        """Generate geometric pattern focused lightshow."""
        
        strong_beats = self.beat_data['strong_peaks_ms']
        strongest_hits = self.beat_data['strongest_hits']
        
        # Start black
        self.add_frame(0, 'fill', color=COLORS['black'])
        
        # ===== INTRO (0-12s) =====
        self.add_persistent_snowflake(16, COLORS['white'], 500, 10000)
        
        # Expanding square on first strong hit (1230ms)
        self.add_expanding_square(1230, 16, 3)
        
        # More snowflakes
        self.add_persistent_snowflake(10, COLORS['cyan'], 4000, 12000)
        self.add_persistent_snowflake(22, COLORS['ice_blue'], 6000, 12000)
        
        # Dual squares at 7732ms
        self.add_dual_expanding_squares(7732)
        
        # Smooth wave
        self.add_wave_sweep(9000, 'right', COLORS['purple'], 50)
        
        # ===== MAIN THEME 1 (12-36s) =====
        # Shorter text "WIZARD" (fits better)
        self.add_text_short("WIZARD", 5, 12000, 2000)
        
        # Expanding square at 14187ms
        self.add_expanding_square(14187, 16, 3)
        
        # Snowflakes
        self.add_persistent_snowflake(8, COLORS['white'], 16000, 18000)
        self.add_persistent_snowflake(16, COLORS['cyan'], 18000, 18000)
        self.add_persistent_snowflake(24, COLORS['ice_blue'], 20000, 18000)
        
        # Expanding squares on strong beats
        self.add_expanding_square(20665, 12, 3)
        self.add_concentric_rings(23000, 20)
        self.add_dual_expanding_squares(27120)
        self.add_expanding_square(30139, 16, 3)
        
        # Waves
        self.add_wave_sweep(25000, 'right', COLORS['magenta'], 40)
        self.add_wave_sweep(32000, 'left', COLORS['cyan'], 40)
        
        # ===== BREAKDOWN (36-60s) - Piano =====
        # Many snowflakes
        for i in range(6):
            x = 5 + i * 4
            self.add_persistent_snowflake(x, COLORS['white'], 36000 + i * 2000, 20000)
        
        # Rotating square for piano section
        self.add_rotating_square(40000, 16000, 16)
        
        # Expanding squares on beats
        self.add_expanding_square(38452, 16, 3)
        self.add_concentric_rings(44907, 10)
        self.add_expanding_square(47949, 22, 4)
        self.add_concentric_rings(53823, 16)
        
        # Gentle waves
        self.add_wave_sweep(50000, 'right', COLORS['ice_blue'], 60)
        self.add_wave_sweep(55000, 'left', COLORS['purple'], 60)
        
        # ===== MAIN THEME 2 (60-84s) =====
        self.add_text_short("WIZARD", 5, 60000, 2000)
        
        # More snowflakes
        for i in range(5):
            x = 6 + i * 5
            self.add_persistent_snowflake(x, COLORS['cyan'], 64000 + i * 1500, 18000)
        
        # Expanding squares
        self.add_dual_expanding_squares(66000)
        self.add_expanding_square(74025, 12, 3)
        self.add_expanding_square(75418, 20, 4)
        
        # Rotating squares
        self.add_rotating_square(70000, 12000, 16)
        
        # Waves
        self.add_wave_sweep(68000, 'right', COLORS['bright_magenta'], 35)
        self.add_wave_sweep(76000, 'left', COLORS['cyan'], 35)
        self.add_wave_sweep(80000, 'right', COLORS['purple'], 35)
        
        # ===== BRIDGE (84-108s) =====
        self.add_text_short("WIZRD", 6, 84000, 2000)
        
        # Maximum snowflakes
        for i in range(8):
            x = 4 + i * 3
            self.add_persistent_snowflake(x, COLORS['white'], 88000 + i * 1000, 18000)
        
        # Many expanding squares
        self.add_expanding_square(90209, 16, 3)
        self.add_dual_expanding_squares(94644)
        self.add_concentric_rings(96664, 16)
        self.add_expanding_square(100000, 12, 4)
        self.add_expanding_square(103000, 20, 3)
        
        # Rotating squares
        self.add_rotating_square(92000, 14000, 16)
        
        # Waves
        for i in range(4):
            self.add_wave_sweep(98000 + i * 2000, 'right' if i % 2 == 0 else 'left', 
                              COLORS['bright_magenta'], 30)
        
        # ===== CLIMAX (108-144s) =====
        self.add_text_short("WIZARD", 5, 108000, 2500)
        
        # ALL snowflakes
        for i in range(10):
            x = 3 + i * 2
            self.add_persistent_snowflake(x, COLORS['cyan'], 112000 + i * 1000, 25000)
        
        # MANY expanding squares
        for i in range(10):
            x = 8 + (i * 10) % 20
            self.add_expanding_square(115000 + i * 2500, x, 3)
        
        # Dual squares
        self.add_dual_expanding_squares(120000)
        self.add_dual_expanding_squares(125000)
        
        # Big square on strongest hit (130426ms)
        self.add_expanding_square(130426, 16, 3)
        self.add_expanding_square(130426, 8, 3)
        self.add_expanding_square(130426, 24, 3)
        
        # More patterns
        self.add_concentric_rings(135000, 16)
        self.add_expanding_square(138716, 16, 3)
        
        # Rotating squares
        self.add_rotating_square(128000, 14000, 16)
        
        # Waves
        for i in range(8):
            self.add_wave_sweep(118000 + i * 2000, 'right' if i % 2 == 0 else 'left',
                              COLORS['bright_white'] if i % 3 == 0 else COLORS['magenta'], 25)
        
        # ===== FINAL RIFFS (144-168s) - EPIC! =====
        # Clear for dramatic effect
        self.add_frame(144000, 'fill', color=COLORS['dim_blue'])
        
        # MASSIVE expanding squares from all positions
        self.add_expanding_square(144300, 8, 3)
        self.add_expanding_square(144300, 16, 3)
        self.add_expanding_square(144300, 24, 3)
        
        self.add_text_short("WIZARD", 5, 145000, 1800)
        
        # Continuous snowflakes
        for i in range(10):
            x = 3 + i * 2
            self.add_persistent_snowflake(x, COLORS['white'], 148000 + i * 600, 15000)
        
        # MANY expanding squares (this is the epic part)
        for i in range(15):
            x = 6 + (i * 8) % 24
            self.add_expanding_square(150000 + i * 1000, x, 3)
        
        # Dual squares repeatedly
        self.add_dual_expanding_squares(152000)
        self.add_dual_expanding_squares(155000)
        self.add_dual_expanding_squares(158000)
        self.add_dual_expanding_squares(161000)
        self.add_dual_expanding_squares(164000)
        
        # Concentric rings
        self.add_concentric_rings(153000, 12)
        self.add_concentric_rings(157000, 20)
        self.add_concentric_rings(162000, 16)
        
        # Rotating squares
        self.add_rotating_square(154000, 12000, 16)
        
        # Fast waves
        for i in range(8):
            self.add_wave_sweep(156000 + i * 1200, 'right' if i % 2 == 0 else 'left',
                              COLORS['bright_magenta'] if i % 2 == 0 else COLORS['cyan'], 25)
        
        # ===== OUTRO (168-186s) =====
        self.add_frame(168000, 'fill', color=COLORS['deep_blue'])
        
        # Cascading white from top
        for wave in range(8):
            t = 169000 + wave * 180
            for y in range(HEIGHT):
                row = get_row_leds(y)
                self.add_frame(t + y * 120, 'set', color=COLORS['bright_white'], leds=row)
                if y > 0:
                    prev = get_row_leds(y - 1)
                    self.add_frame(t + y * 120 + 50, 'set', color=COLORS['ice_blue'], leds=prev)
        
        # Scroll "WIZARD"
        self.add_frame(176000, 'fill', color=COLORS['dim_blue'])
        
        text = "WIZARD"
        fonts = {
            'W': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,5),(2,4),(3,5),(4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
            'I': [(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6)],
            'Z': [(0,0),(1,0),(2,0),(3,0),(3,1),(2,2),(2,3),(1,4),(0,5),(0,6),(1,6),(2,6),(3,6)],
            'A': [(1,0),(2,0),(0,1),(3,1),(0,2),(3,2),(0,3),(1,3),(2,3),(3,3),(0,4),(3,4),(0,5),(3,5),(0,6),(3,6)],
            'R': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,1),(1,3),(2,3),(2,4),(3,5),(3,6)],
            'D': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,1),(3,2),(3,3),(3,4),(3,5),(1,6),(2,6)],
        }
        
        for frame in range(80):
            x_pos = 32 - frame
            if -30 < x_pos < 32:
                leds = []
                x_off = 0
                for char in text:
                    if char in fonts:
                        for dx, dy in fonts[char]:
                            led = xy_to_led(x_pos + x_off + dx, dy)
                            if led >= 0:
                                leds.append(led)
                        x_off += 5
                if leds:
                    self.add_frame(176500 + frame * 100, 'set', color=COLORS['bright_white'], leds=leds)
        
        # END WITH BLACK
        self.add_frame(184000, 'fill', color=COLORS['dim_blue'])
        self.add_frame(185000, 'fill', color=COLORS['black'])
        self.add_frame(185829, 'fill', color=COLORS['black'])
        
        self.frames.sort(key=lambda f: f['timestampMs'])
        
        return {
            'name': 'Wizards in Winter',
            'description': 'Geometric pattern lightshow with expanding squares, rotating patterns, and persistent snowflakes',
            'durationMs': 185829,
            'frames': self.frames
        }

def main():
    print("Loading beat data...")
    with open('wizards_detailed_analysis.json', 'r') as f:
        beat_data = json.load(f)
    
    print("Generating GEOMETRIC PATTERN lightshow...")
    gen = LightshowGenerator(beat_data)
    lightshow = gen.generate()
    
    output = 'Nutcracker/wwwroot/lights/wizards-in-winter.json'
    with open(output, 'w') as f:
        json.dump(lightshow, f, indent=2)
    
    print(f"\nGenerated: {output}")
    print(f"  Duration: {lightshow['durationMs']}ms (3:05)")
    print(f"  Total Frames: {len(lightshow['frames'])}")
    print(f"\nKEY CHANGES:")
    print(f"  - REMOVED rapid flashing columns (no more headache!)")
    print(f"  - MORE expanding squares/geometric patterns (what you love!)")
    print(f"  - Added rotating squares and concentric rings")
    print(f"  - Dual expanding squares from multiple points")
    print(f"  - Shorter text: 'WIZARD' or 'WIZRD' (fits on screen)")
    print(f"  - Better beat sync with actual song hits")
    print(f"  - Smooth waves instead of rapid chases")
    print(f"  - ENDS WITH BLACK")
    print(f"\nREADY!")

if __name__ == '__main__':
    main()
