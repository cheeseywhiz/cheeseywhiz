#!/usr/bin/python3
import battery

if __name__ == '__main__':
    string = 'upower -i /org/freedesktop/UPower/devices/battery_BAT0 | grep -E "energy:|energy-full:"'
    cmd = battery.str_cmd(string)
    print(cmd)
