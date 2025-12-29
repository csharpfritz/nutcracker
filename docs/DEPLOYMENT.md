# Nutcracker Deployment Guide

## Quick Deployment (Recommended)

### Incremental Deployment
Use the automated deployment scripts for faster deployments that only upload changed files:

**Windows (PowerShell):**
```bash
.\deploy.ps1
```

**Linux/Mac:**
```bash
./deploy.sh
```

**Options:**
- `--clean` / `-Clean`: Clean rebuild before deployment
- `--skip-build` / `-SkipBuild`: Skip build, deploy existing files only
- `--target` / `-Target`: Target Pi address (default: nutcracker-2)
- `--user` / `-User`: SSH username (default: jfritz)
- `--path` / `-Path`: Remote deployment path (default: /home/jfritz/www)

**Examples:**
```bash
# Standard deployment
.\deploy.ps1

# Clean rebuild and deploy
.\deploy.ps1 -Clean

# Deploy to different Pi
.\deploy.ps1 -Target "192.168.1.100" -User "pi" -Path "/home/pi/nutcracker"

# Deploy only (skip build)
.\deploy.ps1 -SkipBuild
```

### Benefits of Incremental Deployment
- **Fast**: Only uploads changed files (using rsync)
- **Efficient**: Compresses data during transfer
- **Safe**: Automatically restarts service after deployment
- **Smart**: Excludes debug files and development configs

## Manual Deployment

### 1. Build and Deploy
```bash
cd Nutcracker
dotnet publish -c Release
# Uses MSBuild target to automatically deploy via scripts above
```

### 2. Manual SCP (Not Recommended)
```bash
cd Nutcracker
dotnet publish -c Release -r linux-arm64 --self-contained
scp -r bin/Release/net10.0/linux-arm64/publish/* jfritz@nutcracker-2:/home/jfritz/www/
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

## LED Hardware Permissions

The rpi_ws281x library requires elevated permissions to access DMA and GPIO hardware.

### Option 1: Run with sudo (Quick Testing)
```bash
cd /home/jfritz/www
sudo ./Nutcracker
```

### Option 2: Use systemd service (Recommended)
The service configuration above runs as root automatically. Just use:
```bash
sudo systemctl restart nutcracker
sudo journalctl -u nutcracker -f
```

### Option 3: Set Linux Capabilities (Most Secure)
Allow LED control without full root privileges:
```bash
# Upload the capability script
scp set_capabilities.sh jfritz@nutcracker-2:/home/jfritz/www/

# Run it on the Pi
ssh jfritz@nutcracker-2
cd /home/jfritz/www
chmod +x set_capabilities.sh
./set_capabilities.sh

# Now you can run without sudo
./Nutcracker
```

**Note:** Capabilities are lost when the binary is replaced, so re-run `set_capabilities.sh` after each deployment if using this method.

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
