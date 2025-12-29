#!/usr/bin/env python3
"""
LED Driver Bridge Script for Nutcracker
Receives JSON commands via stdin and controls WS2812B LED strip via GPIO 18
"""

import sys
import json
import time
import signal

try:
    import board
    import neopixel
except ImportError:
    print(json.dumps({"error": "Required libraries not found. Install with: pip3 install adafruit-circuitpython-neopixel"}), flush=True)
    sys.exit(1)

class LedDriver:
    def __init__(self, num_leds=256, gpio_pin=board.D18, brightness=0.3):
        self.pixels = neopixel.NeoPixel(gpio_pin, num_leds, brightness=brightness, auto_write=False)
        self.num_leds = num_leds
        print(json.dumps({"status": "initialized", "leds": num_leds}), flush=True)
        
    def clear_all(self):
        """Clear all LEDs"""
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
        
    def set_pixel(self, index, r, g, b):
        """Set a single pixel color"""
        if 0 <= index < self.num_leds:
            self.pixels[index] = (r, g, b)
            
    def set_pixels(self, pixels_data):
        """Set multiple pixels: [{index, r, g, b}, ...]"""
        for pixel in pixels_data:
            idx = pixel.get('index', -1)
            if 0 <= idx < self.num_leds:
                self.pixels[idx] = (
                    pixel.get('r', 0),
                    pixel.get('g', 0),
                    pixel.get('b', 0)
                )
                
    def fill_all(self, r, g, b):
        """Fill all LEDs with color"""
        self.pixels.fill((r, g, b))
        
    def show(self):
        """Update the display"""
        self.pixels.show()
        
    def process_command(self, command):
        """Process a command from JSON"""
        cmd_type = command.get('command')
        
        if cmd_type == 'clear':
            self.clear_all()
            return {"status": "ok", "command": "clear"}
            
        elif cmd_type == 'set_pixel':
            self.set_pixel(
                command.get('index', 0),
                command.get('r', 0),
                command.get('g', 0),
                command.get('b', 0)
            )
            return {"status": "ok", "command": "set_pixel"}
            
        elif cmd_type == 'set_pixels':
            self.set_pixels(command.get('pixels', []))
            return {"status": "ok", "command": "set_pixels", "count": len(command.get('pixels', []))}
            
        elif cmd_type == 'fill':
            self.fill_all(
                command.get('r', 0),
                command.get('g', 0),
                command.get('b', 0)
            )
            return {"status": "ok", "command": "fill"}
            
        elif cmd_type == 'show':
            self.show()
            return {"status": "ok", "command": "show"}
            
        elif cmd_type == 'ping':
            return {"status": "ok", "command": "ping"}
            
        else:
            return {"status": "error", "message": f"Unknown command: {cmd_type}"}

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print(json.dumps({"status": "shutdown"}), flush=True)
    sys.exit(0)

def main():
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize LED driver
        driver = LedDriver(num_leds=256, brightness=0.3)
        
        # Clear LEDs on startup
        driver.clear_all()
        
        # Process commands from stdin (one JSON object per line)
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                command = json.loads(line)
                result = driver.process_command(command)
                print(json.dumps(result), flush=True)
            except json.JSONDecodeError as e:
                print(json.dumps({"status": "error", "message": f"Invalid JSON: {str(e)}"}), flush=True)
            except Exception as e:
                print(json.dumps({"status": "error", "message": str(e)}), flush=True)
                
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Fatal error: {str(e)}"}), flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
