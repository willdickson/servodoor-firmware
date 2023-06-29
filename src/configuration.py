import json
import constants

class Configuration:

    MAX_ERROR_MSGS = 5 

    def __init__(self):
        self.error = False
        self.error_msgs = [] 
        self.servo_data = self.load()
        self.servo_list = self.create_servo_list()

    def add_error_msg(self,msg):
        if len(self.error_msgs) < self.MAX_ERROR_MSGS:
            self.error_msgs.append(msg)

    def clear_error_msgs(self):
        self.error_msgs.clear()

    def has_errors(self):
        return bool(self.error_msgs)

    def load(self):
        data = None
        try:
            with open(constants.CONFIG_FILE, 'r') as f:
                data = json.load(f)
        except OSError as err:
            self.add_error_msg('config.json not found')
        except ValueError as err:
            self.add_error_msg('config.json parse error')
        finally:
            if data is None:
                data = constants.DEFAULT_CONFIG_DICT
        return data

    def create_servo_list(self):
        servo_list = []
        for door_name, door_data in self.servo_data.items():
            try:
                servo_num = int(door_data['servo'])
            except (TypeError, ValueError) as err:
                self.error = True
                self.add_error_msg('servo_num not integer')
                continue

            try:
                servo = constants.SERVO_MAP[servo_num]
            except IndexError as err: 
                self.error = True
                self.add_error_msgs('servo num out of range')
                continue

            door_data['index'] = len(servo_list)
            servo_list.append(servo)
        return servo_list
                


