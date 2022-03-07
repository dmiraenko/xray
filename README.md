# xray

Work-in-progress terminal program to control x-ray tubes

## Known Issues

1. Functions still not tested on actual hardware.
2. Manual is not clear on some commands. There are ':' sybols where they don't make sense.
3. How does DBF3003 respond to the `WT:`, `ID:`, `SW:05`, `DS:` commands?

## Usage Manual

1. `set` - sets values on the device.
    1. `port` - select which port corresponds to the DBF3003 device.
    2. `ma <xx>` set current (mA).
    3. `kv <xx>` - set voltage (kV).
    4. `kvma <xx> <xx>` - set both voltage (first, kV) and current (second, mA).
    5. `power <xxxx>` - set power output (W).
    6. `focus <list>` - select aperture focus from list of suggestions.
    7. `material <list>` - select anode material from list of suggestions.
    8. `waterflow <xxx>` - set operating point for water flow (Hz).
    9. `tube <x>` - change selected tube number.
    10. `warmup <list> <yy>` - select warm-up time from list and test voltage (kV) for currently selected tube.
    11. `timer <x> <hh> <mm> <ss>` - set timer for tube number `x`.
    12. `language <list>` - select device language from list of suggestions.
    13. `date <DD> <MM> <YY> <hh> <mm> <ss>` or `date current` - set date on the device.
2. `read` - reads values from the device.
    1. `kvma` - read setpoint and actual voltage and current values.
    2. `power` - read power output (W).
    3. `focus` - read aperture focus.
    4. `material`- read anode material.
    5. `waterflow` - read minimum and current water flow rate (Hz).
    6. `tube` - read selected tube number, warm-up time left, and elapsed operating hours.
    7. `timer <x>` - read setpoint and current timer value for provided tube number.
    8. `msg` - read messsage fromt he device.
    9. `id` - read device ID.
    10. `date` - read device-set date.
3. Commands for toggling state.
    1. `voltage <on/off>` - turns high voltage on the anode on/off. If there is an error in this command, it sends an OFF signal by default.
    2. `shutter <open/close> <x>` - opens/closes shutter with provided number.
    3. `timer <on/off> <x>` - starts/stops timer with provided number.
4. Other commands.
    1. `status` - outputs a general status report of the device state.
    2. `stop` - exits the program.
