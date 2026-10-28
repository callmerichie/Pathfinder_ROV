#!/bin/bash
# Geekworm X728 power button daemon, ported to libgpiod v2.
# Event-driven: gpiomon sleeps until the shutdown pin changes, instead of polling it with gpioget (~5% of a core).
# Usage: xPWR.sh <gpio_chip> <shutdown_pin> <boot_pin>   e.g. xPWR.sh 0 5 12

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <gpio_chip> <shutdown_pin> <boot_pin>"
  exit 1
fi

GPIOCHIP=$1
SHUTDOWN=$2
BOOT=$3

REBOOTPULSEMINIMUM=200   # ms; shorter pulses are noise
SHUTDOWNTIMEOUT=0.6      # s; pin still high after this = shutdown request

# Tell the X728 the Pi has booted; v2 gpioset keeps running to hold the line, so run it in the background
gpioset -c "$GPIOCHIP" "$BOOT"=1 &

now_ms() { date +%s%3N; }

# %e prints 1 for a rising edge, 2 for falling; stdbuf makes gpiomon print each event immediately into the pipe
stdbuf -oL gpiomon -c "$GPIOCHIP" -e both -F "%e" "$SHUTDOWN" | while read -r edge; do
  [ "$edge" = "1" ] || continue
  pulseStart=$(now_ms)

  # Wait for the falling edge, but not forever: the X728 holds the pin high to request a shutdown
  read -r -t "$SHUTDOWNTIMEOUT" edge
  rc=$?
  if [ $rc -gt 128 ]; then
    echo "Shutdown signal on pin $SHUTDOWN, halting Pi..."
    poweroff
    exit
  elif [ $rc -ne 0 ]; then
    break   # gpiomon exited; let systemd restart the service
  fi

  if [ $(( $(now_ms) - pulseStart )) -gt $REBOOTPULSEMINIMUM ]; then
    echo "Reboot signal on pin $SHUTDOWN, rebooting Pi..."
    reboot
    exit
  fi
done

echo "gpiomon stopped, exiting"
exit 1
