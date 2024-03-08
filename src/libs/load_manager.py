#from .io_ports_mock import *
from .io_ports import *


class LoadManager:

    def __init__(self):
        print("LoadManager : init")

        self.boards   = [0x20, 0x21]
        self.io_ports = IOPorts(self.boards)

        self.priority_board  = [1, 0, 1, 0, 1, 0]
        self.priority_pin    = [0, 0, 1, 1, 2, 2]
        self.state           = [0, 0, 0, 0, 0, 0]

        self.load_level   = 0
        self.is_change    = True
        self.logger       = ""

        self.remove_all()

    def led_on(self, led_id):
        self.io_ports.set(led_id, 3)

    def led_off(self, led_id):
        self.io_ports.clear(led_id, 3)

    def remove_all(self):
        #print("remove_all ", self.state)

        #turn off all outputs
        for i in range(len(self.state)):
            if self.state[i] != 0:
                self.state[i] = 0
                self.is_change = True

        self._update_state()


    def remove_load(self):
        #print("remove_load ", self.state)

        #turn off last running
        for i in reversed(range(len(self.state))):
            if self.state[i] != 0:
                self.state[i] = 0
                self.is_change = True
                break

        self._update_state()


    def add_load(self):
        #print("add_load ", self.state)

        #turn on first not running
        for i in range(len(self.state)):
            if self.state[i] == 0:
                self.state[i] = 1
                self.is_change = True
                break
        
        self._update_state()


    def change(self):
        result = self.is_change
        self.is_change = False

        return result
    
    def get_log(self):
        result = ""
        result+= str(self.state) + " "

        return result
    

    def _update_state(self):
        for i in range(len(self.state)):
            if self.state[i] != 0:
                self.io_ports.set(self.priority_board[i], self.priority_pin[i])
            else:
                self.io_ports.clear(self.priority_board[i], self.priority_pin[i])

