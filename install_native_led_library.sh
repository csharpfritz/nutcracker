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

# Build the library with shared library support
scons

# Check what was built
echo "Built files:"
ls -la *.a *.so* 2>/dev/null || echo "No shared library found, will create one"

# Create shared library from static library if needed
if [ ! -f "libws2811.so" ] && [ -f "libws2811.a" ]; then
    echo "Creating shared library from static library..."
    gcc -shared -Wl,--whole-archive libws2811.a -Wl,--no-whole-archive -o libws2811.so.1.0.0
    ln -sf libws2811.so.1.0.0 libws2811.so.1
    ln -sf libws2811.so.1 libws2811.so
fi

# Install the library
if [ -f "libws2811.so.1.0.0" ]; then
    sudo cp libws2811.so.1.0.0 /usr/local/lib/
    sudo ln -sf /usr/local/lib/libws2811.so.1.0.0 /usr/local/lib/libws2811.so.1
    sudo ln -sf /usr/local/lib/libws2811.so.1 /usr/local/lib/libws2811.so
elif [ -f "libws2811.so.1" ]; then
    sudo cp libws2811.so.1 /usr/local/lib/
    sudo ln -sf /usr/local/lib/libws2811.so.1 /usr/local/lib/libws2811.so
else
    echo "ERROR: Could not create shared library"
    exit 1
fi

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
