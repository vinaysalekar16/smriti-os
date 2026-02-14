#!/bin/bash

echo "SMRITI OTA: Checking for updates..."

cd /home/vinay/smriti-os || exit

# fetch latest info
git fetch origin main

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "SMRITI OTA: Already up to date"
    exit 0
fi

echo "SMRITI OTA: Update found!"
echo "SMRITI OTA: Pulling update..."

git pull origin main

echo "SMRITI OTA: Restarting kiosk..."
sudo systemctl restart kiosk.service
