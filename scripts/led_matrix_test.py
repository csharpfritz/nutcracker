#!/usr/bin/env python3
"""
SPI LED Matrix Test Script for Raspberry Pi
SPI Pin: GPIO 10 (SPI0 MOSI) - Data line
For WS2812B/NeoPixel-style LED strips or matrices using SPI
"""

import time
import sys
try:
    import RPi.GPIO as GPIO
    import spidev
    import board
    import neopixel
except ImportError:
    print("Required libraries not found. Install with:")
    print("pip3 install RPi.GPIO spidev adafruit-circuitpython-neopixel")
    sys.exit(1)

def create_device():
    """Initialize the LED strip/matrix device"""
    try:
        # Assuming 8x32 = 256 LEDs in a matrix
        # Try GPIO 10 (Pin 19) first - SPI MOSI pin
        print("Attempting GPIO 10 (Pin 19 - SPI MOSI)...")
        pixels = neopixel.NeoPixel(board.D10, 256, brightness=0.1, auto_write=False)
        print("✓ NeoPixel device initialized on GPIO 10 (SPI MOSI)")
        print("Connections needed:")
        print("VCC -> Pin 2 or 4 (5V)")
        print("GND -> Pin 6, 9, 14, 20, 25, 30, 34, or 39 (GND)") 
        print("DIN -> Pin 19 (GPIO 10 - SPI0 MOSI)")
        return pixels
    except Exception as e:
        print(f"✗ GPIO 10 failed: {e}")
        print("Trying GPIO 18 (Pin 12 - PWM) as fallback...")
        try:
            pixels = neopixel.NeoPixel(board.D18, 256, brightness=0.1, auto_write=False)
            print("✓ NeoPixel device initialized on GPIO 18 (PWM)")
            print("Connections needed:")
            print("VCC -> Pin 2 or 4 (5V)")
            print("GND -> Pin 6, 9, 14, 20, 25, 30, 34, or 39 (GND)") 
            print("DIN -> Pin 12 (GPIO 18 - PWM)")
            return pixels
        except Exception as e2:
            print(f"✗ GPIO 18 also failed: {e2}")
            print("Both GPIO 10 and GPIO 18 failed. Check connections and permissions.")
            return None

def test_basic_display(pixels):
    """Test basic LED patterns across full 8x32 matrix"""
    print("Testing basic LED display across full 8x32 matrix...")
    
    # Clear all pixels
    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(1)
    
    # Fill entire matrix with red
    print("Filling entire matrix with red...")
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(2)
    
    # Fill entire matrix with green
    print("Filling entire matrix with green...")
    pixels.fill((0, 255, 0))
    pixels.show()
    time.sleep(2)
    
    # Fill entire matrix with blue
    print("Filling entire matrix with blue...")
    pixels.fill((0, 0, 255))
    pixels.show()
    time.sleep(2)
    
    # Test individual rows (8 rows)
    print("Testing individual rows...")
    pixels.fill((0, 0, 0))
    for row in range(8):
        # Light up one row at a time
        pixels.fill((0, 0, 0))
        for col in range(32):
            pixel_index = row * 32 + col
            pixels[pixel_index] = (255, 255, 255)  # White
        pixels.show()
        time.sleep(0.5)
    
    # Test individual columns (32 columns)
    print("Testing individual columns...")
    pixels.fill((0, 0, 0))
    for col in range(32):
        # Light up one column at a time
        pixels.fill((0, 0, 0))
        for row in range(8):
            pixel_index = row * 32 + col
            pixels[pixel_index] = (255, 255, 255)  # White
        pixels.show()
        time.sleep(0.1)

def test_patterns(pixels):
    """Test various LED patterns across full 8x32 matrix"""
    print("Testing LED patterns across full matrix...")
    
    # Horizontal rainbow stripes (8 rows, different colors)
    print("Horizontal rainbow stripes...")
    colors = [
        (255, 0, 0),    # Red
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Yellow
        (0, 255, 0),    # Green
        (0, 255, 255),  # Cyan
        (0, 0, 255),    # Blue
        (75, 0, 130),   # Indigo
        (148, 0, 211),  # Violet
    ]
    
    pixels.fill((0, 0, 0))
    for row in range(8):
        color = colors[row]
        for col in range(32):
            pixel_index = row * 32 + col
            pixels[pixel_index] = color
    pixels.show()
    time.sleep(3)
    
    # Vertical rainbow stripes (divide 32 columns into color sections)
    print("Vertical rainbow stripes...")
    pixels.fill((0, 0, 0))
    cols_per_color = 32 // len(colors)  # 4 columns per color
    for col in range(32):
        color_index = min(col // cols_per_color, len(colors) - 1)
        color = colors[color_index]
        for row in range(8):
            pixel_index = row * 32 + col
            pixels[pixel_index] = color
    pixels.show()
    time.sleep(3)
    
    # Moving wave across the matrix
    print("Moving wave pattern...")
    for wave_pos in range(40):  # Move wave across and off screen
        pixels.fill((0, 0, 0))
        for row in range(8):
            for col in range(32):
                # Create a sine wave effect
                distance_from_wave = abs(col - wave_pos)
                if distance_from_wave < 5:  # Wave width of 5 pixels
                    brightness = max(0, 255 - (distance_from_wave * 51))  # Fade effect
                    pixel_index = row * 32 + col
                    pixels[pixel_index] = (0, brightness, brightness)
        pixels.show()
        time.sleep(0.1)
    
    # Scanning dot pattern
    print("Scanning dot pattern...")
    pixels.fill((0, 0, 0))
    for pixel_index in range(256):  # All 256 LEDs
        if pixel_index > 0:
            pixels[pixel_index - 1] = (0, 0, 0)  # Turn off previous
        pixels[pixel_index] = (255, 255, 255)  # Turn on current
        pixels.show()
        time.sleep(0.02)  # Faster scan
    
    # Checkerboard pattern
    print("Checkerboard pattern...")
    pixels.fill((0, 0, 0))
    for row in range(8):
        for col in range(32):
            pixel_index = row * 32 + col
            # Checkerboard logic: alternating pattern
            if (row + col) % 2 == 0:
                pixels[pixel_index] = (255, 0, 0)  # Red
            else:
                pixels[pixel_index] = (0, 0, 255)  # Blue
    pixels.show()
    time.sleep(3)
    
    # Border outline
    print("Border outline...")
    pixels.fill((0, 0, 0))
    for row in range(8):
        for col in range(32):
            pixel_index = row * 32 + col
            # Light up border pixels
            if row == 0 or row == 7 or col == 0 or col == 31:
                pixels[pixel_index] = (0, 255, 0)  # Green border
    pixels.show()
    time.sleep(3)
    
    # Pulsing effect
    print("Pulsing effect...")
    for pulse in range(3):  # 3 pulses
        for brightness in range(0, 256, 5):  # Fade in
            pixels.fill((brightness, 0, brightness))  # Purple
            pixels.show()
            time.sleep(0.02)
        for brightness in range(255, -1, -5):  # Fade out
            pixels.fill((brightness, 0, brightness))  # Purple
            pixels.show()
            time.sleep(0.02)
    
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
        # Clear all LEDs and close SPI
        pixels.fill((0, 0, 0))
        pixels.show()
        pixels.close()
        print("LEDs cleared and SPI closed")

if __name__ == "__main__":
    main()