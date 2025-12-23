#!/bin/bash
# Install native rpi_ws281x library for WS2812B LED control
# This script installs the C library that the C# P/Invoke code calls

echo "Installing rpi_ws281x native library for WS2812B LED control..."

# Update package lists
sudo apt-get update

# Install build dependencies
sudo apt-get install -y git scons build-essential

# Clone and build rpi_ws281x library
cd /tmp
if [ -d "rpi_ws281x" ]; then
    rm -rf rpi_ws281x
fi

git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x

# Build the library
scons

# Install the library
sudo cp libws2811.so.1 /usr/local/lib/
sudo ln -sf /usr/local/lib/libws2811.so.1 /usr/local/lib/libws2811.so
sudo ldconfig

# Copy header for reference
sudo cp ws2811.h /usr/local/include/

echo "Installation complete!"
echo ""
echo "Library installed to: /usr/local/lib/libws2811.so"
echo ""
echo "Note: Your application needs to run with sudo or the following permissions:"
echo "  sudo setcap 'cap_dma=ep cap_sys_admin=ep' /path/to/Nutcracker"
echo ""
echo "Alternatively, run the application with sudo."
