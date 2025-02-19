import numpy
import smbus

import time


def check_devices(channel, device = [0x20, 0x21]):
    bus = smbus.SMBus(channel)

    detected_devices = []
    errors = []
    for adr in device:
        try:
            #output to zero
            bus.write_byte_data(adr, 0x01, 0)
            detected_devices.append(adr)
            
            result_str = "I2C OK for " + str(bus) + " " + str(channel) + " " + str(adr)            
            print(result_str)
        except:
            result_str = "error i2c communicating on bus " + str(bus) + " " + str(channel) + " " + str(adr)            
            errors.append(result_str)
            print(result_str)

    return detected_devices, errors


class IOPorts:
    def __init__(self, channel, device = [0x20, 0x21]):
        self.bus = smbus.SMBus(channel)

        self.devices = device
        self.output = []

        for adr in self.devices:
            #output to zero
            self.bus.write_byte_data(adr, 0x01, 0)

            #no polarity inversion
            self.bus.write_byte_data(adr, 0x02, 0)
            
            #config as output
            self.bus.write_byte_data(adr, 0x03, 0)

            self.output.append(0x00)

    
    def set(self, board_id, output_id):
        
        self.output[board_id]|= 1<<output_id 

        adr = self.devices[board_id]        
        self.bus.write_byte_data(adr, 0x01, self.output[board_id])
      
    def clear(self, board_id, output_id):
        self.output[board_id]&=~(1<<output_id)
        
        adr = self.devices[board_id]
        self.bus.write_byte_data(adr, 0x01, self.output[board_id])


if __name__ == "__main__":
    boards   = [0x20, 0x21]
    io_boards = IOPorts(boards)

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
