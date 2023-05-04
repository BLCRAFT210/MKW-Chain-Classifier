#!/bin/bash
# Restart dolphin script if it has crashed or if 120 seconds have gone by, likely indicating a freeze

while true; do
    if [ ! $(pgrep dolphin-emu) ]; then
        timeout -s SIGKILL 120 dolphin-emu --script /home/brian/MKW-Chain-Classifier/ghostreplay.py -e /home/brian/Documents/MKW/RMCP01.iso
    fi
    sleep 1
done
