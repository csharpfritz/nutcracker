#!/usr/bin/env python3
"""
Wizards in Winter - IMPRESSIVE VERSION
Based on actual song analysis with proper section alignment
"""

import json
from typing import List

WIDTH = 32
HEIGHT = 8

def xy_to_led(x: int, y: int) -> int:
    """Convert matrix coordinates to LED index for serpentine wiring."""
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
    def __init__(self):
        self.frames = []
        
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
        # Fall (1 second)
        for step in range(6):
            y = step + 1
            if y < HEIGHT - 1:
                leds = self.get_snowflake(x, y)
                self.add_frame(start + step * 150, 'set', color=color, leds=leds)
                if step > 0:
                    prev = self.get_snowflake(x, step)
                    self.add_frame(start + step * 150 + 50, 'set', color=COLORS['dim_blue'], leds=prev)
        
        # Stay visible
        final_y = min(6, HEIGHT - 2)
        final_leds = self.get_snowflake(x, final_y)
        for t in range(0, duration, 3000):
            self.add_frame(start + 900 + t, 'set', color=color, leds=final_leds)
        
        # Fade out
        self.add_frame(start + 900 + duration, 'set', color=COLORS['ice_blue'], leds=final_leds)
        self.add_frame(start + 900 + duration + 300, 'set', color=COLORS['dim_blue'], leds=final_leds)
    
    def add_explosive_burst(self, t: int, center_x: int = 16):
        """Explosive radial burst from center."""
        for r in range(1, 10):
            leds = []
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    if abs(x - center_x) + abs(y - 3) == r:
                        led = xy_to_led(x, y)
                        if led >= 0:
                            leds.append(led)
            colors = [COLORS['bright_white'], COLORS['bright_magenta'], COLORS['magenta'], 
                     COLORS['purple'], COLORS['ice_blue'], COLORS['deep_blue']]
            color = colors[min(r - 1, len(colors) - 1)]
            if leds:
                self.add_frame(t + r * 30, 'set', color=color, leds=leds)
    
    def add_rapid_column_chase(self, start: int, duration: int, color1: str, color2: str):
        """Super fast alternating column chase."""
        step_time = 60
        steps = duration // step_time
        for step in range(steps):
            t = start + step * step_time
            # Even columns
            even_leds = []
            for x in range(0, WIDTH, 2):
                even_leds.extend(get_column_leds(x))
            # Odd columns
            odd_leds = []
            for x in range(1, WIDTH, 2):
                odd_leds.extend(get_column_leds(x))
            
            if step % 2 == 0:
                self.add_frame(t, 'set', color=color1, leds=even_leds)
                self.add_frame(t + 10, 'set', color=color2, leds=odd_leds)
            else:
                self.add_frame(t, 'set', color=color2, leds=even_leds)
                self.add_frame(t + 10, 'set', color=color1, leds=odd_leds)
    
    def add_wave_sweep(self, start: int, direction: str, color: str, speed: int = 40):
        """Wave that sweeps across display."""
        if direction == 'right':
            for x in range(WIDTH):
                leds = get_column_leds(x)
                self.add_frame(start + x * speed, 'set', color=color, leds=leds)
        else:
            for x in range(WIDTH - 1, -1, -1):
                leds = get_column_leds(x)
                self.add_frame(start + (WIDTH - 1 - x) * speed, 'set', color=color, leds=leds)
    
    def add_spiral_vortex(self, start: int):
        """Spiraling vortex from center outward."""
        spiral_order = [15, 16, 14, 17, 13, 18, 12, 19, 11, 20, 10, 21, 9, 22, 8, 23, 7, 24, 6, 25, 5, 26, 4, 27, 3, 28, 2, 29, 1, 30, 0, 31]
        colors = [COLORS['magenta'], COLORS['bright_magenta'], COLORS['purple'], COLORS['cyan']]
        for i, x in enumerate(spiral_order):
            color = colors[i % len(colors)]
            leds = get_column_leds(x)
            self.add_frame(start + i * 50, 'set', color=color, leds=leds)
    
    def add_text_flash(self, text: str, x: int, start: int, hold: int):
        """Flash text with bold font."""
        fonts = {
            'W': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,4),(1,5),(1,6),(2,3),(2,4),(2,5),(2,6),(3,4),(3,5),(3,6),(4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
            'I': [(0,0),(1,0),(2,0),(3,0),(1,1),(2,1),(1,2),(2,2),(1,3),(2,3),(1,4),(2,4),(1,5),(2,5),(0,6),(1,6),(2,6),(3,6)],
            'Z': [(0,0),(1,0),(2,0),(3,0),(4,0),(3,1),(4,1),(2,2),(3,2),(1,3),(2,3),(0,4),(1,4),(0,5),(0,6),(1,6),(2,6),(3,6),(4,6)],
            'A': [(1,0),(2,0),(3,0),(0,1),(1,1),(3,1),(4,1),(0,2),(4,2),(0,3),(1,3),(2,3),(3,3),(4,3),(0,4),(4,4),(0,5),(4,5),(0,6),(4,6)],
            'R': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,0),(4,1),(4,2),(1,3),(2,3),(3,3),(2,4),(3,4),(3,5),(4,5),(3,6),(4,6)],
            'D': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,0),(4,1),(4,2),(4,3),(4,4),(4,5),(1,6),(2,6),(3,6)],
            'S': [(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(1,3),(2,3),(3,3),(4,4),(4,5),(0,6),(1,6),(2,6),(3,6)]
        }
        
        def display_text(color: str, t: int):
            leds = []
            x_off = 0
            for char in text:
                if char in fonts:
                    for dx, dy in fonts[char]:
                        led = xy_to_led(x + x_off + dx, dy)
                        if led >= 0:
                            leds.append(led)
                    x_off += 6
            if leds:
                self.add_frame(t, 'set', color=color, leds=leds)
        
        # Flash sequence
        display_text(COLORS['purple'], start)
        display_text(COLORS['dim_blue'], start + 120)
        display_text(COLORS['magenta'], start + 240)
        display_text(COLORS['dim_blue'], start + 360)
        display_text(COLORS['bright_magenta'], start + 480)
        display_text(COLORS['bright_white'], start + 600)
        
        # Hold
        for t in range(0, hold, 400):
            display_text(COLORS['bright_white'], start + 700 + t)
        
        # Fade
        display_text(COLORS['white'], start + 700 + hold)
        display_text(COLORS['cyan'], start + 700 + hold + 200)
        display_text(COLORS['ice_blue'], start + 700 + hold + 400)
        display_text(COLORS['dim_blue'], start + 700 + hold + 600)
    
    def generate(self):
        """Generate the impressive lightshow based on actual song analysis."""
        
        # Start black
        self.add_frame(0, 'fill', color=COLORS['black'])
        
        # ===== INTRO (0-12s) - Building energy, bells =====
        # Single snowflake intro
        self.add_persistent_snowflake(16, COLORS['white'], 500, 8000)
        
        # Explosive burst on strongest hit at 1230ms
        self.add_explosive_burst(1230, 16)
        
        # Build with gentle waves
        self.add_wave_sweep(3000, 'right', COLORS['ice_blue'], 50)
        self.add_wave_sweep(4500, 'left', COLORS['purple'], 50)
        
        # More snowflakes
        self.add_persistent_snowflake(8, COLORS['cyan'], 6000, 10000)
        self.add_persistent_snowflake(24, COLORS['white'], 7500, 10000)
        
        # Building burst at 7732ms
        self.add_explosive_burst(7732, 10)
        self.add_explosive_burst(7732, 22)
        
        # ===== MAIN THEME 1 (12-36s) - Fast guitar riffs =====
        # "WIZARDS" text
        self.add_text_flash("WIZARDS", 2, 12000, 2500)
        
        # Explosive burst at 14187ms (strong hit)
        self.add_explosive_burst(14187, 16)
        
        # INTENSE rapid column chase
        self.add_rapid_column_chase(16000, 8000, COLORS['bright_magenta'], COLORS['cyan'])
        
        # Multiple snowflakes
        self.add_persistent_snowflake(6, COLORS['white'], 18000, 15000)
        self.add_persistent_snowflake(16, COLORS['cyan'], 20000, 15000)
        self.add_persistent_snowflake(26, COLORS['ice_blue'], 22000, 15000)
        
        # Bursts on strong hits
        self.add_explosive_burst(20665, 12)
        self.add_explosive_burst(27120, 20)
        self.add_explosive_burst(28746, 24)
        self.add_explosive_burst(30139, 8)
        
        # Spiral vortex
        self.add_spiral_vortex(25000)
        
        # Fast waves
        self.add_wave_sweep(32000, 'right', COLORS['bright_white'], 30)
        self.add_wave_sweep(33200, 'left', COLORS['magenta'], 30)
        self.add_wave_sweep(34400, 'right', COLORS['cyan'], 30)
        
        # ===== BREAKDOWN (36-60s) - Piano section =====
        # More snowflakes (many visible at once)
        self.add_persistent_snowflake(4, COLORS['white'], 36000, 20000)
        self.add_persistent_snowflake(12, COLORS['cyan'], 38000, 20000)
        self.add_persistent_snowflake(20, COLORS['ice_blue'], 40000, 20000)
        self.add_persistent_snowflake(28, COLORS['white'], 42000, 18000)
        
        # Burst at 38452ms (strong hit)
        self.add_explosive_burst(38452, 16)
        
        # Gentle alternating columns for piano
        self.add_rapid_column_chase(44000, 12000, COLORS['purple'], COLORS['ice_blue'])
        
        # Bursts on hits
        self.add_explosive_burst(44907, 10)
        self.add_explosive_burst(46532, 22)
        self.add_explosive_burst(47949, 16)
        
        # Waves
        self.add_wave_sweep(50000, 'right', COLORS['cyan'], 45)
        self.add_wave_sweep(52000, 'left', COLORS['purple'], 45)
        self.add_wave_sweep(54000, 'right', COLORS['ice_blue'], 45)
        self.add_wave_sweep(56000, 'left', COLORS['magenta'], 45)
        
        # Bursts
        self.add_explosive_burst(53823, 14)
        self.add_explosive_burst(55843, 18)
        
        # ===== MAIN THEME 2 (60-84s) - Guitar returns =====
        # "WIZARD" text again
        self.add_text_flash("WIZARDS", 2, 60000, 2500)
        
        # INTENSE rapid chase
        self.add_rapid_column_chase(64000, 16000, COLORS['bright_magenta'], COLORS['bright_white'])
        
        # More snowflakes
        self.add_persistent_snowflake(8, COLORS['white'], 65000, 15000)
        self.add_persistent_snowflake(16, COLORS['cyan'], 67000, 15000)
        self.add_persistent_snowflake(24, COLORS['ice_blue'], 69000, 15000)
        
        # Bursts
        self.add_explosive_burst(74025, 12)
        self.add_explosive_burst(75418, 20)
        
        # Spiral
        self.add_spiral_vortex(72000)
        
        # Fast waves
        self.add_wave_sweep(76000, 'right', COLORS['bright_magenta'], 25)
        self.add_wave_sweep(77200, 'left', COLORS['cyan'], 25)
        self.add_wave_sweep(78400, 'right', COLORS['bright_white'], 25)
        self.add_wave_sweep(79600, 'left', COLORS['magenta'], 25)
        self.add_wave_sweep(80800, 'right', COLORS['purple'], 25)
        self.add_wave_sweep(82000, 'left', COLORS['ice_blue'], 25)
        
        # ===== BRIDGE (84-108s) - Building intensity =====
        # "WINTER" text
        self.add_text_flash("WINTER", 3, 84000, 2500)
        
        # Maximum snowflakes
        for i in range(8):
            x = 4 + i * 3
            self.add_persistent_snowflake(x, COLORS['white'], 88000 + i * 1000, 18000)
        
        # Bursts
        self.add_explosive_burst(90209, 16)
        self.add_explosive_burst(94644, 10)
        self.add_explosive_burst(96664, 22)
        
        # Ultra fast chase
        self.add_rapid_column_chase(90000, 16000, COLORS['bright_magenta'], COLORS['cyan'])
        
        # Multiple spirals
        self.add_spiral_vortex(92000)
        self.add_spiral_vortex(98000)
        self.add_spiral_vortex(104000)
        
        # Fast waves
        for i in range(6):
            self.add_wave_sweep(100000 + i * 1200, 'right' if i % 2 == 0 else 'left', 
                              COLORS['bright_white'], 22)
        
        # ===== PEAK/CLIMAX (108-144s) - MAXIMUM ENERGY =====
        # "WIZARDS" AGAIN
        self.add_text_flash("WIZARDS", 2, 108000, 3000)
        
        # ALL snowflakes visible
        for i in range(10):
            x = 3 + i * 2
            self.add_persistent_snowflake(x, COLORS['cyan'], 112000 + i * 1000, 25000)
        
        # CONTINUOUS rapid chase
        self.add_rapid_column_chase(115000, 25000, COLORS['bright_magenta'], COLORS['bright_white'])
        
        # Burst at strongest hit (130426ms)
        self.add_explosive_burst(130426, 16)
        self.add_explosive_burst(130426, 8)
        self.add_explosive_burst(130426, 24)
        
        # Burst at 138716ms
        self.add_explosive_burst(138716, 16)
        
        # Multiple spirals
        for i in range(6):
            self.add_spiral_vortex(118000 + i * 4000)
        
        # Ultra fast waves
        for i in range(12):
            color = [COLORS['bright_white'], COLORS['bright_magenta'], COLORS['cyan'], COLORS['purple']][i % 4]
            self.add_wave_sweep(120000 + i * 1000, 'right' if i % 2 == 0 else 'left', color, 20)
        
        # ===== FINAL RIFFS (144-168s) - EPIC GUITAR FINALE =====
        # THIS IS THE SECTION THAT NEEDS TO BE EPIC!
        
        # Clear everything for dramatic restart
        self.add_frame(144000, 'fill', color=COLORS['dim_blue'])
        
        # Massive burst to start
        for offset in [0, 8, 16, 24]:
            self.add_explosive_burst(144200 + offset * 50, offset)
        
        # "WIZARDS" one more time
        self.add_text_flash("WIZARDS", 2, 145000, 2000)
        
        # INSANE rapid chase (fastest yet)
        self.add_rapid_column_chase(148000, 18000, COLORS['bright_white'], COLORS['bright_magenta'])
        
        # Continuous spiral vortexes
        for i in range(5):
            self.add_spiral_vortex(150000 + i * 3000)
        
        # Ultra rapid waves (overlapping)
        for i in range(15):
            colors = [COLORS['bright_white'], COLORS['bright_magenta'], COLORS['cyan']]
            self.add_wave_sweep(152000 + i * 800, 'right' if i % 2 == 0 else 'left', colors[i % 3], 18)
        
        # Multiple simultaneous bursts
        for i in range(8):
            x = 4 + i * 3
            self.add_explosive_burst(155000 + i * 1200, x)
        
        # Final snowflake cascade
        for i in range(10):
            x = 3 + i * 2
            self.add_persistent_snowflake(x, COLORS['white'], 158000 + i * 600, 8000)
        
        # ===== OUTRO (168-186s) - Wind down/end =====
        # Gentle fade with cascading effect
        self.add_frame(168000, 'fill', color=COLORS['deep_blue'])
        
        # White pixel blizzard from top
        for wave in range(8):
            t = 169000 + wave * 180
            for y in range(HEIGHT):
                row = get_row_leds(y)
                self.add_frame(t + y * 120, 'set', color=COLORS['bright_white'], leds=row)
                if y > 0:
                    prev = get_row_leds(y - 1)
                    self.add_frame(t + y * 120 + 50, 'set', color=COLORS['ice_blue'], leds=prev)
        
        # Scrolling "WIZARDS IN WINTER"
        self.add_frame(176000, 'fill', color=COLORS['dim_blue'])
        
        # Simple scroll text (W I Z A R D S)
        text = "WIZARDS IN WINTER"
        for frame in range(120):
            x_pos = 32 - frame
            # Only display if on screen
            if -30 < x_pos < 32:
                leds = []
                x_off = 0
                for char in text:
                    fonts = {
                        'W': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,4),(1,5),(1,6),(2,3),(2,4),(2,5),(2,6),(3,4),(3,5),(3,6),(4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
                        'I': [(0,0),(1,0),(2,0),(3,0),(1,1),(2,1),(1,2),(2,2),(1,3),(2,3),(1,4),(2,4),(1,5),(2,5),(0,6),(1,6),(2,6),(3,6)],
                        'Z': [(0,0),(1,0),(2,0),(3,0),(4,0),(3,1),(4,1),(2,2),(3,2),(1,3),(2,3),(0,4),(1,4),(0,5),(0,6),(1,6),(2,6),(3,6),(4,6)],
                        'A': [(1,0),(2,0),(3,0),(0,1),(1,1),(3,1),(4,1),(0,2),(4,2),(0,3),(1,3),(2,3),(3,3),(4,3),(0,4),(4,4),(0,5),(4,5),(0,6),(4,6)],
                        'R': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,0),(4,1),(4,2),(1,3),(2,3),(3,3),(2,4),(3,4),(3,5),(4,5),(3,6),(4,6)],
                        'D': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,0),(4,1),(4,2),(4,3),(4,4),(4,5),(1,6),(2,6),(3,6)],
                        'S': [(1,0),(2,0),(3,0),(4,0),(0,1),(0,2),(1,3),(2,3),(3,3),(4,4),(4,5),(0,6),(1,6),(2,6),(3,6)],
                        'N': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,1),(1,2),(2,2),(2,3),(2,4),(3,4),(3,5),(4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
                        'T': [(0,0),(1,0),(2,0),(3,0),(4,0),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(1,1),(3,1)],
                        'E': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,0),(4,0),(1,3),(2,3),(3,3),(1,6),(2,6),(3,6),(4,6)],
                        ' ': []
                    }
                    
                    if char in fonts:
                        for dx, dy in fonts[char]:
                            led = xy_to_led(x_pos + x_off + dx, dy)
                            if led >= 0:
                                leds.append(led)
                        x_off += 6
                
                if leds:
                    self.add_frame(176500 + frame * 70, 'set', color=COLORS['bright_white'], leds=leds)
        
        # CRITICAL: End with BLACK and ensure lightshow stops
        self.add_frame(184500, 'fill', color=COLORS['dim_blue'])
        self.add_frame(185500, 'fill', color=COLORS['black'])
        self.add_frame(185829, 'fill', color=COLORS['black'])  # Final frame at exact duration
        
        # Sort frames
        self.frames.sort(key=lambda f: f['timestampMs'])
        
        return {
            'name': 'Wizards in Winter',
            'description': 'IMPRESSIVE winter wizard lightshow with beat-synced animations, persistent snowflakes, and epic finale',
            'durationMs': 185829,
            'frames': self.frames
        }

def main():
    print("Generating IMPRESSIVE Wizards in Winter lightshow...")
    gen = LightshowGenerator()
    lightshow = gen.generate()
    
    output = 'Nutcracker/wwwroot/lights/wizards-in-winter.json'
    with open(output, 'w') as f:
        json.dump(lightshow, f, indent=2)
    
    print(f"\nGenerated: {output}")
    print(f"  Duration: {lightshow['durationMs']}ms (3:05)")
    print(f"  Total Frames: {len(lightshow['frames'])}")
    print(f"  Description: {lightshow['description']}")
    print(f"\nKEY IMPROVEMENTS:")
    print(f"  - Synced to ACTUAL song sections from analysis")
    print(f"  - Explosive bursts on strongest hits (1.23s, 2:10, etc.)")
    print(f"  - EPIC final riffs section (2:24-2:48)")
    print(f"  - ENDS WITH BLACK - no bleed into idle animation")
    print(f"  - Persistent snowflakes throughout")
    print(f"  - Rapid column chases, spirals, and waves")
    print(f"\nREADY TO IMPRESS!")

if __name__ == '__main__':
    main()
