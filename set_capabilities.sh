#!/bin/bash
# Set Linux capabilities to allow LED control without root

APP_PATH="/home/jfritz/www/Nutcracker"

echo "Setting capabilities on $APP_PATH..."

# Grant capabilities:
# CAP_SYS_RAWIO - for /dev/mem access (DMA)
# CAP_DAC_OVERRIDE - for GPIO access
sudo setcap 'cap_sys_rawio,cap_dac_override=+ep' "$APP_PATH"

# Verify
echo ""
echo "Capabilities set:"
getcap "$APP_PATH"

echo ""
echo "You can now run the app without sudo:"
echo "  ./Nutcracker"
