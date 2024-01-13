import numpy
import smbus

import time

class IOPorts:
    def __init__(self, bus, device = [0x20, 0x21]):
        self.bus = bus
        self.devices = device
        self.output = []

        for adr in self.devices:
            #output to zero
            bus.write_byte_data(adr, 0x01, 0)

            #no polarity inversion
            bus.write_byte_data(adr, 0x02, 0)
            
            #config as output
            bus.write_byte_data(adr, 0x03, 0)

            self.output.append(0x00)
    
    def set(self, board_id, output_id):
        
        self.output[board_id]|= 1<<output_id 

        adr = self.devices[board_id]        
        bus.write_byte_data(adr, 0x01, self.output[board_id])
      
    def clear(self, board_id, output_id):
        self.output[board_id]&=~(1<<output_id)
        
        adr = self.devices[board_id]
        bus.write_byte_data(adr, 0x01, self.output[board_id])


if __name__ == "__main__":
    channel = 1

    bus = smbus.SMBus(channel)
            
    print(bus)
    
    boards   = [0x20, 0x21]
    io_boards = IOPorts(bus, boards)

    while True:
        for b in range(len(boards)):   
            for pin in range(4):
                print("testing board ", b, " Y=", pin)
                io_boards.set(b, pin)
                time.sleep(2)
                io_boards.clear(b, pin)
                time.sleep(0.8)
            print()
        print()
    
    #i2c_address = 0x21 #0x21, 0x22 ... 
    
    #reg0, write = 0x00 -> output port
    #bus.write_byte_data(i2c_address, 0x01, out_v)

    print("done")
