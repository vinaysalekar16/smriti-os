#!/bin/bash

echo "SMRITI: Waiting for audio server..."

# Wait until PipeWire is fully running
until pactl info >/dev/null 2>&1; do
    sleep 1
done

echo "SMRITI: PipeWire ready"

# Wait until HDMI sink appears
until pactl list short sinks | grep -q "alsa_output"; do
    sleep 1
done

echo "SMRITI: HDMI sink detected"

# Get HDMI sink name automatically
SINK=$(pactl list short sinks | grep "alsa_output" | awk '{print $2}' | head -n1)

# Set HDMI as default audio output
pactl set-default-sink "$SINK"

# Set volume to 100% just once at boot
pactl set-sink-volume "$SINK" 100%

echo "SMRITI: Default audio set to $SINK"
