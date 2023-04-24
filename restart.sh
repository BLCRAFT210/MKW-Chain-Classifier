#!/bin/bash
# Restart dolphin script if it has crashed

while true; do
    if [ ! $(pgrep dolphin-emu) ]; then
        dolphin-emu --script /home/brian/MKW-Chain-Classifier/ghostreplay.py -e /home/brian/Documents/MKW/RMCP01.iso
    fi
    sleep 1
done