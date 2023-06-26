## servodoor-firmware

Device firmware automatic control of doors using RC servos and Pimoroni's
[Servo 2040](https://shop.pimoroni.com/products/servo-2040) 18-channel servo
controller. 

## Requirements

* [adafruit-ampy](https://github.com/scientifichackers/ampy)

Note, adafruit-ampy can be installed using pip via 

```bash
pip install adafruit-ampy
```

or 

```bash
pip install .
```
from the project's home directory. 


## Uploading firmware

The upload.py found in the projects top level directory can be used to upload
the firmware and optionally a door configuration the Servo 2040 device.

```
usage: upload.py [-h] -p PORT [-c CONF]

upload Micropython code to microcontroller using ampy

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  device port, e.g. /dev/ttyACM0, COM1, etc.
  -c CONF, --conf CONF  optional configuration file

```

For example, to upload just the firmware to a Servo 2040 device at /dev/ttyACM0
```bash
python upload.py -p /dev/ttyACM0
```

To upload the firmware and an option configuration file. 
```bash
python upload.py -p /dev/ttyACM0 -c /examples/config.json
```

# Door configuration
The door configuration is specified via a .json file containing an object which
specifies the name each door, e.g. "front", "left", "right".  In addition, for
each door, the  servo number and open/close pwm values (us) are specified. 

```json
{
    "front" : {             
        "servo" : 1,      
        "open"  : 1300, 
        "close" : 1898 
    }, 
    "left" : { 
        "servo" : 2,   
        "open"  : 1290, 
        "close" : 1890 
    }, 
    "right" : { 
        "servo" : 3, 
        "open"  : 1300, 
        "close" : 1890 
    }
}
```







