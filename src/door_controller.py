import servo
import constants
from messaging import Messenger
from configuration import Configuration

class DoorController:

    MAX_ERROR_MSGS = 5 

    def __init__(self):
        self.config = Configuration()
        self.messenger = Messenger()
        self.door_state = {}
        self.setup_doors()
        self.error_msgs = []

    def setup_doors(self):
        """ Setup servo cluster for doors """
        self.doors = servo.ServoCluster(0, 0, self.config.servo_list)
        for name, data in self.config.servo_data.items():
            num = data['index']
            pwm = data['close']
            self.door_state[name] = 'close'
            self.doors.pulse(num, pwm, load=False)
            self.doors.enable(num, load=False)
        self.doors.load()

    def add_error_msg(self,msg):
        """
        Add error message to list of error messages.
        """
        if len(self.error_msgs) < self.MAX_ERROR_MSGS:
            self.error_msgs.append(msg)

    def clear_error_msgs(self):
        self.error_msgs.clear()

    def has_errors(self):
        return bool(self.error_msgs)

    def run(self):
        """ Main run loop for door controller """
        while True:
            self.messenger.update()
            if self.messenger.message:
                self.on_message()

    def send(self, rsp):
        self.messenger.send(rsp)
        self.messenger.reset()

    def on_message(self):
        """ 
        Processes incoming messages, pass to switchyard for actions, and send 
        response to sender.  
        """
        msg = self.messenger.message
        if type(msg) == dict:
            rsp = {'ok': True}
            rsp = self.msg_switchyard(msg)
            if not rsp['ok']:
                rsp['err'] = ','.join(self.error_msgs)
                self.error_msgs.clear()
        else:
            rsp = {'ok': False}
            self.add_error_msg(f'msg is not dict: {msg}')
            rsp = {'ok': False, 'err': msg}
        self.send(rsp)

    def msg_switchyard(self, msg):
        """ Take action based on cmd string """
        try:
            cmd = msg['cmd']
        except KeyError:
            self.add_error_msg('message missing cmd')
            rsp = {'ok': False}
            return rsp
        if cmd == 'set_doors':
            rsp = self.cmd_set_doors(msg)
        elif cmd == 'get_doors':
            rsp = self.cmd_get_doors()
        elif cmd == 'enable':
            rsp = self.cmd_enable()
        elif cmd == 'disable':
            rsp = self.cmd_disable()
        elif cmd == 'is_enabled':
            rsp = self.cmd_is_enabled()
        elif cmd == 'get_config':
            rsp = self.cmd_get_config()
        elif cmd == 'config_errors':
            rsp = self.cmd_config_errors()
        else:
            self.add_error_msg('unknown cmd')
            rsp = {'ok': False}
        return rsp

    def cmd_get_doors(self):
        """ Get the door_state of all the doors.  """
        rsp = {'ok': True, 'doors': self.door_state}
        return rsp

    def cmd_set_doors(self, msg):
        """ Open/close doors according to value dict in msg """
        try:
            msg_value = msg['doors']
        except KeyError:
            self.add_error_msg('cmd_set missing doors')
            rsp = {'ok': False}
            return rsp

        if type(msg_value) != dict:
            self.add_error_msg('cmd_set value must be dict')
            rsp = {'ok': False}
            return rsp

        rsp = {'ok': True}
        for name, position in msg_value.items():
            try: 
                data = self.config.servo_data[name]
            except KeyError:
                self.add_error_msg(f'cmd_set name {name} not found')
                rsp = {'ok': False}
                continue
            try:
                pwm = data[position]
            except KeyError:
                self.add_error_msg(f'cmd_set name {name} not found')
                rsp = {'ok': False}
                continue
            num = data['index']
            self.doors.pulse(num, pwm, load=False)
            self.door_state[name] = position
        self.doors.load()
        rsp['doors'] = self.door_state
        return rsp

    def cmd_enable(self):
        """ Enable all doors """
        for _, data in self.config.servo_data.items():
            self.doors.enable(data['index'], load=False)
        self.doors.load()
        rsp = {'ok': True}
        return rsp

    def cmd_disable(self):
        """ Enable all doors """
        for _, data in self.config.servo_data.items():
            self.doors.disable(data['index'], load=False)
        self.doors.load()
        rsp = {'ok': True}
        return rsp

    def cmd_is_enabled(self):
        """
        Checks the enabled status for all doors. Returns true if all
        doors are enabled, False otherwise.
        """
        is_enabled = True
        for _, data in self.config.servo_data.items():
            is_enabled = is_enabled and bool(self.doors.is_enabled(data['index']))
        rsp = {'ok': True, 'is_enabled': is_enabled}
        return rsp

    def cmd_get_config(self):
        """
        Returns the current door configuration.
        """
        config = {}
        for name, data in self.config.servo_data.items():
            config[name] = {}
            for k, v in data.items():
                if k != 'index':
                    config[name][k] = v
        rsp = {'ok': True, 'config': config}
        return rsp

    def cmd_config_errors(self):
        error_msgs = []
        error_msgs.extend(self.config.error_msgs)
        rsp = {'ok': True, 'config_errors': ','.join(self.error_msgs) }
        return rsp


