import servo
import constants
from messaging import Messenger
from configuration import Configuration

class DoorController:

    MAX_ERROR_MSGS = 5 

    def __init__(self):
        self.config = Configuration()
        self.messenger = Messenger()
        self.state = {}
        self.setup_doors()
        self.error_msgs = []

    def setup_doors(self):
        """ Setup servo cluster for doors """
        self.doors = servo.ServoCluster(0, 0, self.config.servo_list)
        for door_name, door_config in self.config.servo_data.items():
            num = door_config['index']
            pwm = door_config['close']
            self.state[door_name] = 'close'
            self.doors.pulse(num, pwm, load=False)
            self.doors.enable(num, load=False)
        self.doors.load()

    def add_error_msg(self,msg):
        if len(self.error_msgs) < self.MAX_ERROR_MSGS:
            self.error_msgs.append(msg)

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
            try:
                cmd = msg['cmd']
            except KeyError:
                self.add_error_msg('message missing cmd')
                rsp = {'ok': False}
            else:
                rsp = self.msg_switchyard(cmd, msg)
        else:
            self.add_error_msg('msg is not dict')
            rsp = {'ok': False}
        if not rsp['ok']:
            rsp['err'] = ','.join(self.error_msgs)
            self.error_msgs.clear()
        self.send(rsp)

    def msg_switchyard(self, cmd, msg):
        """ Take action based on cmd string """
        if cmd == 'set':
            rsp = self.cmd_set(msg)
        elif cmd == 'get':
            rsp = self.cmd_get(msg)
        else:
            self.add_error_msg('unknown cmd')
            rsp = {'ok': False}
        return rsp


    def cmd_set(self, msg):
        """ Open/close doors according to value dict in msg """
        try:
            msg_value = msg['value']
        except KeyError:
            self.add_error_msg('cmd_set missing value')
            rsp = {'ok': False}
            return rsp

        if type(msg_value) != dict:
            self.add_error_msg('cmd_set value must be dict')
            rsp = {'ok': False}
            return rsp

        rsp = {'ok': True}
        for name, position in msg_value.items():
            try:
                servo_data = self.config.servo_data[name]
            except KeyError:
                self.add_error_msg(f'cmd_set name {name} not found')
                rsp = {'ok': False}
                continue
            try:
                pwm = servo_data[position]
            except KeyError:
                self.add_error_msg(f'cmd_set name {name} not found')
                rsp = {'ok': False}
                continue
            num = servo_data['index']
            self.doors.pulse(num, pwm, load=False)
            self.state[name] = position
        self.doors.load()
        return rsp

    def cmd_get(self, msg):
        rsp = {'ok': True, 'value': self.state}
        return rsp


