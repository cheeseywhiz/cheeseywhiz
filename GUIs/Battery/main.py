#!/usr/bin/python3
"""Battery desktop widget.

Displays graph of battery usage data on desktop."""
import battery

if __name__ == '__main__':
    print(battery.info())
