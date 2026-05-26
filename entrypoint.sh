#!/bin/bash
set -e

rm -f /tmp/.X99-lock

echo "Iniciando display virtual Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 -ac &
export DISPLAY=:99
sleep 3

echo "Iniciando python..."
python main.py
echo "Fim."