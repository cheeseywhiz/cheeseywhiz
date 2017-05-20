#!/bin/bash

batteryinfo=$(upower -i /org/freedesktop/UPower/devices/battery_BAT0)
rm pipe
echo "$batteryinfo" >> pipe
