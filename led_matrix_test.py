#!/usr/bin/env python3
"""
Single-Wire LED Matrix Test Script for Raspberry Pi
GPIO Pin: 18 (PWM0) - Data only
For WS2812B/NeoPixel-style LED strips or matrices
"""

import time
import sys
try:
    import RPi.GPIO as GPIO
    import board
    import neopixel
except ImportError:
    print("Required libraries not found. Install with:")
    print("pip3 install RPi.GPIO adafruit-circuitpython-neopixel")
    sys.exit(1)

def create_device():
    """Initialize the LED strip/matrix device"""
    try:
        # Assuming 8x32 = 256 LEDs in a matrix
        # GPIO 18 is board.D18
        pixels = neopixel.NeoPixel(board.D18, 256, brightness=0.1, auto_write=False)
        print("NeoPixel device initialized on GPIO 18")
        print("Connections needed:")
        print("VCC -> 5V (or 3.3V)")
        print("GND -> GND") 
        print("DIN -> GPIO 18 (Pin 12)")
        return pixels
    except Exception as e:
        print(f"Error initializing NeoPixel device: {e}")
        return None

def test_basic_display(pixels):
    """Test basic LED patterns"""
    print("Testing basic LED display...")
    
    # Clear all pixels
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(1)
    
    # Light up first few LEDs in red
    for i in range(10):
        pixels[i] = (255, 0, 0)
    pixels.show()
    time.sleep(2)
    
    # Clear and light up in green
    pixels.fill((0, 0, 0))
    for i in range(10, 20):
        pixels[i] = (0, 255, 0)
    pixels.show()
    time.sleep(2)
    
    # Clear and light up in blue
    pixels.fill((0, 0, 0))
    for i in range(20, 30):
        pixels[i] = (0, 0, 255)
    pixels.show()
    time.sleep(2)

def test_patterns(pixels):
    """Test various LED patterns"""
    print("Testing LED patterns...")
    
    # Rainbow pattern
    colors = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211),  # Violet
    ]
    
    for i, color in enumerate(colors):
        pixels.fill((0, 0, 0))
        start = i * 10
        end = min(start + 10, len(pixels))
        for j in range(start, end):
            pixels[j] = color
        pixels.show()
        time.sleep(1)
    
    # Moving dot
    print("Moving dot pattern...")
    pixels.fill((0, 0, 0))
    for i in range(min(50, len(pixels))):
        if i > 0:
            pixels[i-1] = (0, 0, 0)  # Turn off previous
        pixels[i] = (255, 255, 255)  # Turn on current
        pixels.show()
        time.sleep(0.1)
    
    # Clear all
    pixels.fill((0, 0, 0))
    pixels.show()

def main():
    """Main test function"""
    print("Single-Wire LED Test Script")
    print("===========================")
    
    # Initialize device
    pixels = create_device()
    if not pixels:
        sys.exit(1)
        
    print(f"Device initialized: {len(pixels)} LEDs")
    
    try:
        # Run tests
        test_basic_display(pixels)
        test_patterns(pixels)
        
        print("All tests completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        # Clear all LEDs
        pixels.fill((0, 0, 0))
        pixels.show()
        print("LEDs cleared")

if __name__ == "__main__":
    main()