import sys
import json
import select


class Messenger:

    def __init__(self):
        self.buffer = []
        self.new_message = False

    def update(self):
        while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)
            if ch == '\n' and self.buffer:
                self.new_message = True
            else:
                self.buffer.append(ch)
    
    @property
    def message(self):
        if self.new_message:
            msg_json = ''.join(self.buffer)
            try:
                msg_dict = json.loads(msg_json)
            except Exception as err:
                return f'{err}'
            else:
                return msg_dict
        else:
            return []

    def reset(self):
        self.new_message = False
        self.buffer = []

    def send(self, msg_dict):
        try:
            print(json.dumps(msg_dict))
        except:
            print('error')
