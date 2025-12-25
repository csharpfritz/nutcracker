#!/usr/bin/env python3
"""
Wizards in Winter - V5 BOLD & SIMPLE
Build the entire show to match the intensity of the successful finale
Focus on BIG, FULL-SCREEN effects with tight music sync
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

def get_all_leds() -> List[int]:
    return list(range(256))

def get_column_leds(x: int) -> List[int]:
    return [xy_to_led(x, y) for y in range(HEIGHT) if xy_to_led(x, y) >= 0]

def get_row_leds(y: int) -> List[int]:
    return [xy_to_led(x, y) for x in range(WIDTH) if xy_to_led(x, y) >= 0]

def get_left_half() -> List[int]:
    leds = []
    for x in range(16):
        leds.extend(get_column_leds(x))
    return leds

def get_right_half() -> List[int]:
    leds = []
    for x in range(16, 32):
        leds.extend(get_column_leds(x))
    return leds

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
    'very_dim_blue': '#001133',
    'black': '#000000'
}

class LightshowGenerator:
    def __init__(self):
        self.frames = []
        
    def add_frame(self, timestamp_ms: int, effect: str, **kwargs):
        frame = {'timestampMs': timestamp_ms, 'effect': effect}
        frame.update(kwargs)
        self.frames.append(frame)
    
    def add_full_flash(self, t: int, color: str, duration: int = 100):
        """Full screen flash - BIG impact."""
        self.add_frame(t, 'fill', color=color)
        self.add_frame(t + duration, 'fill', color=COLORS['dim_blue'])
    
    def add_full_pulse(self, t: int, color: str):
        """Full screen pulse with fade."""
        self.add_frame(t, 'fill', color=color)
        self.add_frame(t + 80, 'fill', color=COLORS['ice_blue'])
        self.add_frame(t + 160, 'fill', color=COLORS['dim_blue'])
    
    def add_left_right_wipe(self, start: int, color: str, speed: int = 30):
        """Simple left-to-right wipe."""
        for x in range(WIDTH):
            leds = get_column_leds(x)
            self.add_frame(start + x * speed, 'set', color=color, leds=leds)
    
    def add_right_left_wipe(self, start: int, color: str, speed: int = 30):
        """Simple right-to-left wipe."""
        for x in range(WIDTH - 1, -1, -1):
            leds = get_column_leds(x)
            self.add_frame(start + (WIDTH - 1 - x) * speed, 'set', color=color, leds=leds)
    
    def add_split_flash(self, t: int, left_color: str, right_color: str):
        """Left half one color, right half another."""
        self.add_frame(t, 'set', color=left_color, leds=get_left_half())
        self.add_frame(t, 'set', color=right_color, leds=get_right_half())
    
    def add_alternating_columns(self, start: int, duration: int, color1: str, color2: str, step_time: int = 250):
        """Gentle alternating columns - NOT rapid."""
        steps = duration // step_time
        for step in range(steps):
            t = start + step * step_time
            even_leds = []
            odd_leds = []
            for x in range(WIDTH):
                if x % 2 == 0:
                    even_leds.extend(get_column_leds(x))
                else:
                    odd_leds.extend(get_column_leds(x))
            
            if step % 2 == 0:
                self.add_frame(t, 'set', color=color1, leds=even_leds)
                self.add_frame(t, 'set', color=color2, leds=odd_leds)
            else:
                self.add_frame(t, 'set', color=color2, leds=even_leds)
                self.add_frame(t, 'set', color=color1, leds=odd_leds)
    
    def add_rising_wave(self, start: int, color: str):
        """Bottom to top wave."""
        for y in range(HEIGHT - 1, -1, -1):
            leds = get_row_leds(y)
            self.add_frame(start + (HEIGHT - 1 - y) * 60, 'set', color=color, leds=leds)
    
    def add_falling_wave(self, start: int, color: str):
        """Top to bottom wave."""
        for y in range(HEIGHT):
            leds = get_row_leds(y)
            self.add_frame(start + y * 60, 'set', color=color, leds=leds)
    
    def add_piano_steps(self, start: int, num_steps: int, color: str):
        """Growing column chart for piano steps - like a bar graph."""
        step_width = 3  # Each column is 3 pixels wide
        step_duration = 200  # ms between steps
        
        for step in range(num_steps):
            t = start + step * step_duration
            height = min(step + 1, HEIGHT)  # Grow taller with each step
            x_start = step * step_width
            
            # Draw column of this height
            leds = []
            for x in range(x_start, min(x_start + step_width, WIDTH)):
                for y in range(HEIGHT - height, HEIGHT):
                    led = xy_to_led(x, y)
                    if led >= 0:
                        leds.append(led)
            
            if leds:
                self.add_frame(t, 'set', color=color, leds=leds)
    
    def add_expanding_square(self, t: int, center_x: int = 16, center_y: int = 3):
        """Expanding square from center."""
        for r in range(1, 12):
            leds = []
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    if abs(x - center_x) + abs(y - center_y) == r:
                        led = xy_to_led(x, y)
                        if led >= 0:
                            leds.append(led)
            
            if r <= 3:
                color = COLORS['bright_white']
            elif r <= 6:
                color = COLORS['bright_magenta']
            elif r <= 9:
                color = COLORS['cyan']
            else:
                color = COLORS['ice_blue']
            
            if leds:
                self.add_frame(t + r * 40, 'set', color=color, leds=leds)
    
    def generate(self):
        """Generate BOLD, SIMPLE lightshow that builds to the perfect finale."""
        
        # Start black
        self.add_frame(0, 'fill', color=COLORS['black'])
        
        # ===== INTRO (0-12s) - Establish the energy =====
        # Opening hit at 1230ms - BIG FLASH
        self.add_full_flash(1230, COLORS['bright_white'], 150)
        
        # Simple build with wipes
        self.add_left_right_wipe(2000, COLORS['cyan'], 20)
        self.add_right_left_wipe(3200, COLORS['magenta'], 20)
        
        # Flash on strong beats
        self.add_full_pulse(4000, COLORS['bright_white'])
        self.add_full_pulse(5500, COLORS['bright_magenta'])
        
        # More wipes building intensity
        self.add_left_right_wipe(6500, COLORS['purple'], 18)
        self.add_expanding_square(7732, 16, 3)
        
        # Build to theme
        self.add_right_left_wipe(9000, COLORS['cyan'], 18)
        self.add_full_pulse(10500, COLORS['bright_white'])
        self.add_left_right_wipe(11000, COLORS['bright_magenta'], 18)
        
        # ===== MAIN THEME 1 (12-36s) - HIGH ENERGY =====
        # Big hit at start
        self.add_full_flash(12000, COLORS['bright_white'], 200)
        
        # Rapid wipes for guitar energy
        self.add_left_right_wipe(13000, COLORS['magenta'], 15)
        self.add_expanding_square(14187, 16, 3)
        self.add_right_left_wipe(15000, COLORS['cyan'], 15)
        
        # Split flashes for intensity
        self.add_split_flash(16500, COLORS['magenta'], COLORS['cyan'])
        self.add_split_flash(16700, COLORS['cyan'], COLORS['magenta'])
        
        # More wipes
        self.add_left_right_wipe(18000, COLORS['bright_white'], 15)
        self.add_full_pulse(19500, COLORS['bright_magenta'])
        
        # Big hit
        self.add_expanding_square(20665, 16, 3)
        self.add_full_flash(21000, COLORS['bright_white'], 150)
        
        # Continue building
        self.add_right_left_wipe(22500, COLORS['purple'], 15)
        self.add_left_right_wipe(24000, COLORS['cyan'], 15)
        
        # Alternating for variation
        self.add_alternating_columns(25500, 2000, COLORS['magenta'], COLORS['cyan'], 250)
        
        # Big hit
        self.add_expanding_square(27120, 16, 3)
        self.add_full_pulse(27500, COLORS['bright_white'])
        
        # Final push of section
        self.add_left_right_wipe(29000, COLORS['bright_magenta'], 15)
        self.add_expanding_square(30139, 16, 3)
        self.add_right_left_wipe(31000, COLORS['cyan'], 15)
        
        # Build to breakdown
        self.add_full_pulse(33000, COLORS['bright_white'])
        self.add_left_right_wipe(34000, COLORS['ice_blue'], 20)
        
        # ===== BREAKDOWN (36-60s) - Piano section with growing steps =====
        # Transition to piano - softer start
        self.add_frame(36000, 'fill', color=COLORS['dim_blue'])
        
        # Piano steps - growing column chart
        self.add_piano_steps(36500, 8, COLORS['cyan'])
        
        # Clear and next piano phrase
        self.add_frame(38500, 'fill', color=COLORS['dim_blue'])
        self.add_piano_steps(39000, 8, COLORS['ice_blue'])
        
        # Another phrase
        self.add_frame(41000, 'fill', color=COLORS['dim_blue'])
        self.add_piano_steps(41500, 8, COLORS['purple'])
        
        # Build
        self.add_frame(43500, 'fill', color=COLORS['dim_blue'])
        self.add_piano_steps(44000, 10, COLORS['magenta'])
        
        # More piano phrases
        self.add_frame(46500, 'fill', color=COLORS['dim_blue'])
        self.add_piano_steps(47000, 8, COLORS['cyan'])
        
        # More piano steps building back up
        self.add_frame(49500, 'fill', color=COLORS['dim_blue'])
        self.add_piano_steps(50000, 10, COLORS['ice_blue'])
        
        # Final piano phrase before guitar return
        self.add_frame(52500, 'fill', color=COLORS['dim_blue'])
        self.add_piano_steps(53000, 10, COLORS['bright_magenta'])
        
        # Transition back to guitar
        self.add_left_right_wipe(55500, COLORS['cyan'], 18)
        self.add_right_left_wipe(57000, COLORS['magenta'], 18)
        self.add_full_pulse(58000, COLORS['bright_white'])
        
        # ===== MAIN THEME 2 (60-84s) - RETURN OF ENERGY =====
        # Big guitar return
        self.add_full_flash(60000, COLORS['bright_white'], 200)
        self.add_left_right_wipe(61500, COLORS['bright_magenta'], 15)
        
        # Rapid wipes
        self.add_right_left_wipe(63000, COLORS['cyan'], 15)
        self.add_left_right_wipe(64500, COLORS['magenta'], 15)
        
        # Split flashes
        self.add_split_flash(66000, COLORS['bright_white'], COLORS['cyan'])
        self.add_split_flash(66200, COLORS['cyan'], COLORS['bright_white'])
        
        # More intensity
        self.add_right_left_wipe(68000, COLORS['bright_magenta'], 15)
        self.add_full_pulse(70000, COLORS['bright_white'])
        self.add_left_right_wipe(71500, COLORS['cyan'], 15)
        
        # Big hits
        self.add_expanding_square(74025, 16, 3)
        self.add_full_flash(74500, COLORS['bright_white'], 150)
        self.add_expanding_square(75418, 16, 3)
        
        # Push forward
        self.add_right_left_wipe(77000, COLORS['magenta'], 15)
        self.add_left_right_wipe(78500, COLORS['cyan'], 15)
        self.add_alternating_columns(80000, 3000, COLORS['bright_magenta'], COLORS['cyan'], 200)
        
        # ===== BRIDGE (84-108s) - BUILDING INTENSITY =====
        # Start building
        self.add_full_flash(84000, COLORS['bright_white'], 200)
        self.add_left_right_wipe(85500, COLORS['bright_magenta'], 15)
        self.add_right_left_wipe(87000, COLORS['cyan'], 15)
        
        # More energy
        self.add_full_pulse(89000, COLORS['bright_white'])
        self.add_expanding_square(90209, 16, 3)
        self.add_left_right_wipe(91000, COLORS['magenta'], 15)
        
        # Split flashes more frequent
        self.add_split_flash(92500, COLORS['bright_white'], COLORS['magenta'])
        self.add_split_flash(92700, COLORS['magenta'], COLORS['bright_white'])
        
        self.add_right_left_wipe(94000, COLORS['cyan'], 15)
        self.add_expanding_square(94644, 16, 3)
        
        # Build build build
        self.add_full_pulse(96000, COLORS['bright_white'])
        self.add_left_right_wipe(97500, COLORS['bright_magenta'], 15)
        self.add_right_left_wipe(99000, COLORS['cyan'], 15)
        
        self.add_expanding_square(100000, 16, 3)
        self.add_full_flash(100500, COLORS['bright_white'], 150)
        
        # Maximum build
        self.add_alternating_columns(102000, 2000, COLORS['bright_magenta'], COLORS['cyan'], 150)
        self.add_expanding_square(103000, 16, 3)
        self.add_left_right_wipe(104500, COLORS['bright_white'], 15)
        self.add_right_left_wipe(106000, COLORS['bright_magenta'], 15)
        
        # ===== CLIMAX (108-144s) - MAXIMUM ENERGY =====
        # HUGE hit
        self.add_full_flash(108000, COLORS['bright_white'], 250)
        
        # Non-stop action
        self.add_left_right_wipe(109500, COLORS['bright_magenta'], 15)
        self.add_right_left_wipe(111000, COLORS['cyan'], 15)
        self.add_full_pulse(112500, COLORS['bright_white'])
        
        self.add_left_right_wipe(114000, COLORS['magenta'], 15)
        self.add_right_left_wipe(115500, COLORS['cyan'], 15)
        
        # Expanding squares more frequent
        self.add_expanding_square(117000, 16, 3)
        self.add_full_flash(117500, COLORS['bright_white'], 150)
        
        # Rapid wipes
        self.add_left_right_wipe(119000, COLORS['bright_magenta'], 15)
        self.add_right_left_wipe(120500, COLORS['cyan'], 15)
        self.add_left_right_wipe(122000, COLORS['bright_white'], 15)
        
        # Split flashes rapid
        for i in range(5):
            t = 124000 + i * 400
            self.add_split_flash(t, COLORS['bright_white'] if i % 2 == 0 else COLORS['magenta'],
                                   COLORS['cyan'] if i % 2 == 0 else COLORS['bright_white'])
        
        # Rising intensity
        self.add_right_left_wipe(126500, COLORS['bright_magenta'], 15)
        self.add_left_right_wipe(128000, COLORS['cyan'], 15)
        
        # HUGE HIT at 130426ms
        self.add_full_flash(130426, COLORS['bright_white'], 300)
        self.add_expanding_square(130426, 16, 3)
        
        # Continue maximum energy
        self.add_left_right_wipe(132000, COLORS['bright_magenta'], 15)
        self.add_right_left_wipe(133500, COLORS['cyan'], 15)
        self.add_full_pulse(135000, COLORS['bright_white'])
        
        self.add_left_right_wipe(136500, COLORS['magenta'], 15)
        self.add_expanding_square(138716, 16, 3)
        self.add_right_left_wipe(139000, COLORS['cyan'], 15)
        
        # Push to finale
        self.add_alternating_columns(140500, 2000, COLORS['bright_white'], COLORS['bright_magenta'], 150)
        self.add_full_pulse(142500, COLORS['bright_white'])
        
        # ===== FINAL RIFFS (144-168s) - EPIC BUILD TO FINALE =====
        # MASSIVE hit
        self.add_full_flash(144000, COLORS['bright_white'], 300)
        
        # Non-stop wipes
        self.add_left_right_wipe(145500, COLORS['bright_magenta'], 12)
        self.add_right_left_wipe(147000, COLORS['cyan'], 12)
        self.add_left_right_wipe(148500, COLORS['bright_white'], 12)
        
        # Expanding squares
        self.add_expanding_square(150000, 16, 3)
        self.add_full_pulse(150500, COLORS['bright_white'])
        
        # Rapid fire
        self.add_right_left_wipe(152000, COLORS['bright_magenta'], 12)
        self.add_left_right_wipe(153500, COLORS['cyan'], 12)
        self.add_right_left_wipe(155000, COLORS['bright_white'], 12)
        
        # Build build build
        self.add_expanding_square(156500, 16, 3)
        self.add_full_flash(157000, COLORS['bright_white'], 200)
        
        # Split flashes rapid
        for i in range(6):
            t = 158500 + i * 300
            self.add_split_flash(t, COLORS['bright_white'] if i % 2 == 0 else COLORS['bright_magenta'],
                                   COLORS['cyan'] if i % 2 == 0 else COLORS['bright_white'])
        
        # Maximum wipes
        self.add_left_right_wipe(161000, COLORS['bright_magenta'], 12)
        self.add_right_left_wipe(162500, COLORS['cyan'], 12)
        self.add_expanding_square(164000, 16, 3)
        
        # Final build
        self.add_full_pulse(165000, COLORS['bright_white'])
        self.add_left_right_wipe(166000, COLORS['bright_magenta'], 12)
        self.add_right_left_wipe(167000, COLORS['bright_white'], 12)
        
        # ===== OUTRO (168-186s) - SNOWSTORM FINALE =====
        # Dark purple background
        self.add_frame(168000, 'fill', color=COLORS['purple'])
        
        # Falling snow - white pixels falling from top like a snowstorm
        # Create multiple falling snowflakes at staggered times
        import random
        random.seed(42)  # Consistent pattern
        
        snow_pixels = []
        for i in range(80):  # 80 individual snowflakes
            x = random.randint(0, WIDTH - 1)
            start_time = 168500 + i * 80  # Stagger starts
            
            # Each pixel falls from top to bottom
            for y in range(HEIGHT):
                t = start_time + y * 100
                led = xy_to_led(x, y)
                if led >= 0:
                    self.add_frame(t, 'set', color=COLORS['bright_white'], leds=[led])
        
        # Build up to full white screen gradually
        # Add more density as we approach the end
        for wave in range(5):
            t = 175000 + wave * 400
            # Random columns light up
            for i in range(8):
                x = random.randint(0, WIDTH - 1)
                leds = get_column_leds(x)
                self.add_frame(t + i * 50, 'set', color=COLORS['bright_white'], leds=leds)
        
        # Transition to full bright white screen
        self.add_frame(177500, 'fill', color=COLORS['white'])
        self.add_frame(178000, 'fill', color=COLORS['bright_white'])
        
        # Scroll "WIZARDS IN WINTER" across the white screen
        text = "WIZARDS IN WINTER"
        fonts = {
            'W': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,5),(2,4),(3,5),(4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
            'I': [(1,0),(1,1),(1,2),(1,3),(1,4),(1,5),(1,6)],
            'Z': [(0,0),(1,0),(2,0),(3,0),(3,1),(2,2),(2,3),(1,4),(0,5),(0,6),(1,6),(2,6),(3,6)],
            'A': [(1,0),(2,0),(0,1),(3,1),(0,2),(3,2),(0,3),(1,3),(2,3),(3,3),(0,4),(3,4),(0,5),(3,5),(0,6),(3,6)],
            'R': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,1),(1,3),(2,3),(2,4),(3,5),(3,6)],
            'D': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,0),(2,0),(3,1),(3,2),(3,3),(3,4),(3,5),(1,6),(2,6)],
            'S': [(1,0),(2,0),(3,0),(0,1),(0,2),(1,3),(2,3),(3,4),(3,5),(0,6),(1,6),(2,6)],
            'N': [(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(1,2),(2,3),(3,4),(4,0),(4,1),(4,2),(4,3),(4,4),(4,5),(4,6)],
            'T': [(0,0),(1,0),(2,0),(3,0),(4,0),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6)],
            'E': [(0,0),(1,0),(2,0),(3,0),(0,1),(0,2),(0,3),(1,3),(2,3),(0,4),(0,5),(0,6),(1,6),(2,6),(3,6)],
            ' ': [],  # Space character
        }
        
        # Text scrolls from right to left with dark blue color to contrast white background
        for frame in range(140):
            x_pos = 35 - frame
            if -95 < x_pos < 35:  # Extended range for full text
                # First fill with white
                self.add_frame(178500 + frame * 70, 'fill', color=COLORS['bright_white'])
                
                # Then draw text in dark blue for contrast
                leds = []
                x_off = 0
                for char in text:
                    if char in fonts:
                        for dx, dy in fonts[char]:
                            led = xy_to_led(x_pos + x_off + dx, dy)
                            if led >= 0:
                                leds.append(led)
                        x_off += 6 if char != ' ' else 3  # Smaller space for space char
                if leds:
                    self.add_frame(178500 + frame * 70, 'set', color=COLORS['deep_blue'], leds=leds)
        
        # END WITH BLACK (perfect ending)
        self.add_frame(184000, 'fill', color=COLORS['dim_blue'])
        self.add_frame(185000, 'fill', color=COLORS['black'])
        self.add_frame(185829, 'fill', color=COLORS['black'])
        
        self.frames.sort(key=lambda f: f['timestampMs'])
        
        return {
            'name': 'Wizards in Winter',
            'description': 'BOLD full-screen lightshow building to the perfect finale',
            'durationMs': 185829,
            'frames': self.frames
        }

def main():
    print("Generating BOLD & SIMPLE lightshow...")
    gen = LightshowGenerator()
    lightshow = gen.generate()
    
    output = 'Nutcracker/wwwroot/lights/wizards-in-winter.json'
    with open(output, 'w') as f:
        json.dump(lightshow, f, indent=2)
    
    print(f"\n✓ Generated: {output}")
    print(f"  Duration: {lightshow['durationMs']}ms (3:05)")
    print(f"  Total Frames: {len(lightshow['frames'])}")
    print(f"\nDESIGN PHILOSOPHY:")
    print(f"  - BIG, SIMPLE effects throughout")
    print(f"  - Full-screen flashes on major hits")
    print(f"  - Left-right wipes for guitar energy")
    print(f"  - Rising/falling waves for piano")
    print(f"  - Expanding squares for impact")
    print(f"  - Builds intensity from intro → climax → EPIC finale")
    print(f"  - PRESERVES the perfect finale (168-186s)")
    print(f"\nREADY TO DEPLOY!")

if __name__ == '__main__':
    main()
