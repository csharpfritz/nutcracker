# Quick Deployment Guide

## On Raspberry Pi

### 1. Install Native LED Library
```bash
chmod +x install_native_led_library.sh
./install_native_led_library.sh
```

### 2. Deploy Application
From your development machine:
```bash
cd Nutcracker
dotnet publish -c Release -r linux-arm64 --self-contained
scp -r bin/Release/net10.0/linux-arm64/publish/* pi@your-pi-address:/home/pi/nutcracker/
```

Or use the built-in deployment target:
```bash
dotnet publish -c Release
# Automatically deploys via SCP (see Nutcracker.csproj)
```

### 3. Run Application
```bash
ssh pi@your-pi-address
cd /home/pi/nutcracker
sudo ./Nutcracker
```

### 4. Set Up Auto-Start (Optional)
Create a systemd service:
```bash
sudo nano /etc/systemd/system/nutcracker.service
```

Contents:
```ini
[Unit]
Description=Nutcracker Holiday Display
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/nutcracker
ExecStart=/home/pi/nutcracker/Nutcracker
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable nutcracker
sudo systemctl start nutcracker
```

View logs:
```bash
sudo journalctl -u nutcracker -f
```

## Verify Installation

Check library is installed:
```bash
ls -l /usr/local/lib/libws2811.so
```

Check application has permissions:
```bash
getcap ./Nutcracker
# Should show: cap_dma,cap_sys_admin=ep
```

Test GPIO access:
```bash
sudo ./Nutcracker --urls http://0.0.0.0:5000
# Should see "LED strip initialized successfully" in logs
```

## Testing Without Full Deploy

Quick test with Python script:
```bash
python3 led_matrix_test.py
```

This verifies:
- Hardware wiring is correct
- GPIO 18 is accessible
- LED strip is functioning
- Power supply is adequate

## Common Issues

**"libws2811.so not found"**
```bash
# Make sure it's in the library path
sudo ldconfig
ls -l /usr/local/lib/libws2811.so
```

**"Permission denied" or "Cannot access /dev/mem"**
```bash
# Run with sudo or set capabilities
sudo ./Nutcracker
```

**LEDs don't light up but no errors**
- Check power supply (most common issue)
- Verify GPIO 18 connection
- Try the Python test script to verify hardware
- Check LED strip color order (GRB vs RGB)
