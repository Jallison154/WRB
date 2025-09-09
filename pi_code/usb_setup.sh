#!/bin/bash
# USB Auto-mounting Setup Script for Raspberry Pi

echo "Setting up USB auto-mounting for WRB Audio Server..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Install required packages
echo "Installing required packages..."
apt update
apt install -y usbutils udisks2

# Create mount point
echo "Creating mount point..."
mkdir -p /media/usb
chmod 755 /media/usb

# Add user to plugdev group for USB access
echo "Adding user to plugdev group..."
usermod -a -G plugdev pi

# Create udev rule for automatic mounting
echo "Creating udev rule..."
cat > /etc/udev/rules.d/99-usb-audio.rules << 'EOF'
# USB Audio Drive Auto-mount Rule
SUBSYSTEM=="block", KERNEL=="sd*", ATTRS{removable}=="1", ACTION=="add", RUN+="/bin/mkdir -p /media/usb/%k", RUN+="/bin/mount -o uid=pi,gid=pi,umask=0002 /dev/%k /media/usb/%k"
SUBSYSTEM=="block", KERNEL=="sd*", ATTRS{removable}=="1", ACTION=="remove", RUN+="/bin/umount -l /media/usb/%k", RUN+="/bin/rmdir /media/usb/%k"
EOF

# Reload udev rules
echo "Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger

# Create audio_files directory on USB drives
echo "Creating audio_files directory template..."
mkdir -p /media/usb/audio_files
chmod 755 /media/usb/audio_files

# Set up GPIO permissions
echo "Setting up GPIO permissions..."
usermod -a -G gpio pi

# Create systemd service for audio server
echo "Creating systemd service..."
cat > /etc/systemd/system/wrb-audio.service << 'EOF'
[Unit]
Description=WRB Audio Server with USB Auto-mounting
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/WRB/pi_code
ExecStart=/usr/bin/python3 audio_server.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/pi/WRB/pi_code

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
echo "Enabling WRB Audio service..."
systemctl daemon-reload
systemctl enable wrb-audio.service

echo "USB auto-mounting setup complete!"
echo ""
echo "Next steps:"
echo "1. Reboot the Pi: sudo reboot"
echo "2. Connect a USB drive with audio files in 'audio_files' directory"
echo "3. Check status: systemctl status wrb-audio.service"
echo "4. View logs: journalctl -u wrb-audio.service -f"
echo ""
echo "LED Status Patterns:"
echo "- 1 blink: System ready"
echo "- 2 blinks: USB mounted successfully"
echo "- 3 blinks: USB mount error"
echo "- 5 blinks: System error"
echo "- Solid on: Audio playing"
