import servo 

CONFIG_FILE = 'config.json'

DEFAULT_CONFIG_DICT = { 
        "A" : { 
            "servo" : 1, 
            "open"  : 1300, 
            "close" : 1898 
            }, 
        "B" : { 
            "servo" : 2,   
            "open"  : 1290, 
            "close" : 1890 
            }, 
        "C" : { 
            "servo" : 3, 
            "open"  : 1300, 
            "close" : 1890 
            } 
        }


SERVO_MAP = {
        1: servo.servo2040.SERVO_1, 
        2: servo.servo2040.SERVO_2, 
        3: servo.servo2040.SERVO_3, 
        4: servo.servo2040.SERVO_4, 
        5: servo.servo2040.SERVO_5, 
        6: servo.servo2040.SERVO_6, 
        7: servo.servo2040.SERVO_7, 
        8: servo.servo2040.SERVO_8, 
        9: servo.servo2040.SERVO_9, 
        10: servo.servo2040.SERVO_10, 
        11: servo.servo2040.SERVO_11, 
        12: servo.servo2040.SERVO_12, 
        13: servo.servo2040.SERVO_13, 
        14: servo.servo2040.SERVO_14, 
        15: servo.servo2040.SERVO_15, 
        16: servo.servo2040.SERVO_16, 
        17: servo.servo2040.SERVO_17, 
        18: servo.servo2040.SERVO_18, 
        }
