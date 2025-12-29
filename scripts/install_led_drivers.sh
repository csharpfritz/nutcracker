#!/bin/bash
# LED Matrix Driver Installation Script for Raspberry Pi
# This script installs the necessary drivers and libraries for an 8x32 LED matrix

echo "LED Matrix Driver Installation"
echo "=============================="

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip if not already installed
echo "Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-dev python3-setuptools

# Install required system libraries
echo "Installing system libraries..."
sudo apt install -y libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libopenjp2-7 libtiff5-dev

# Enable SPI interface
echo "Enabling SPI interface..."
sudo raspi-config nonint do_spi 0

# Install luma.led_matrix library and dependencies
echo "Installing luma.led_matrix library..."
pip3 install --user luma.led_matrix luma.core luma.oled pillow

# Install additional useful libraries
echo "Installing additional libraries..."
pip3 install --user numpy RPi.GPIO spidev

# Create a simple test to verify SPI is working
echo "Creating SPI verification script..."
cat > /tmp/spi_test.py << 'EOF'
#!/usr/bin/env python3
import spidev
import sys

try:
    spi = spidev.SpiDev()
    spi.open(0, 0)  # Bus 0, Device 0
    spi.max_speed_hz = 8000000
    print("SPI interface is available and working!")
    spi.close()
except Exception as e:
    print(f"SPI interface error: {e}")
    print("Make sure SPI is enabled in raspi-config")
    sys.exit(1)
EOF

# Make it executable and run
chmod +x /tmp/spi_test.py
python3 /tmp/spi_test.py

echo ""
echo "Installation completed!"
echo ""
echo "Hardware connections for 8x32 LED matrix:"
echo "VCC -> 5V    (Pin 2 or 4)"
echo "GND -> GND   (Pin 6, 9, 14, 20, 25, 30, 34, or 39)"
echo "DIN -> GPIO 10 (Pin 19 - SPI0 MOSI)"
echo "CS  -> GPIO 8  (Pin 24 - SPI0 CE0)"
echo "CLK -> GPIO 11 (Pin 23 - SPI0 SCLK)"
echo ""
echo "To test your matrix, copy led_matrix_test.py to your Pi and run:"
echo "python3 led_matrix_test.py"
echo ""
echo "If you get permission errors, you may need to add your user to the spi group:"
echo "sudo usermod -a -G spi $USER"
echo "Then log out and back in."