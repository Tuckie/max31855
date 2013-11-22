Python driver for [MAX31855 Cold-Junction Compensated Thermocouple-to-Digital Converter](http://www.maximintegrated.com/datasheet/index.mvp/id/7273)

Requires:
- The [GPIO Library](https://code.google.com/p/raspberry-gpio-python/) (Already on most Raspberry Pi OS builds)
- A [Raspberry Pi](http://www.raspberrypi.org/)

## Basic use

```python

#!/usr/bin/python
from max31855 import MAX31855, MAX31855Error

cs_pin = 24
clock_pin = 23
data_pin = 22
units = "f"
thermocouple = MAX31855(cs_pin, clock_pin, data_pin, units)
print(thermocouple.get())
thermocouple.cleanup()

```

*Note: these are the GPIO pin numbers, not the header pin numbers.*  
*This can be overriden by passing `GPIO.BOARD` as the fifth [init parameter](https://github.com/Tuckie/max31855/blob/master/max31855.py#L11).*

See max31855.py for a multi-chip example.

## Changelog

### V2.0

- SPI now done in software
    - Use whatever pins you want for CS, Clock & Data
    - Hardware SPI was limited to only two chip / slave select lines.  
      Now use as many chips a you have extra pins!
- Removed quick2wire dependency.
- Removed bitstring dependency; bit extraction and two's complement conversion now done in library.
- Added `cleanup()` method to be called on close (or destruction of instance), which does a targeted version of `GPIO.cleanup()`.

NOTE: If you were using the previous hardware-based version, you will have to update your code to match the new init function:
`MAX31855(cs_pin, clock_pin, data_pin, units)`

### V1.0

- Initial release.
