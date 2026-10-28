#!/bin/bash
# Geekworm X728 software shutdown, ported to libgpiod v2.
# Usage: xSoft.sh <gpio_chip> <button_pin>   e.g. xSoft.sh 0 26

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <gpio_chip> <button_pin>" >&2
  exit 1
fi

GPIOCHIP=$1
BUTTON=$2

echo "Your device will be shutting down in 2 seconds..."

# Pin high for 2 s, then back low and exit (-t 2s,0); leaving it low keeps the button / AUTO ON working next time
gpioset -c "$GPIOCHIP" -t 2s,0 "$BUTTON"=1
