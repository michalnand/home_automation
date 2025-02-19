
def check_devices(channel = 1, device = [0x20, 0x21]):
    detected_devices = []
    for adr in device:
        detected_devices.append(adr)
        
    return detected_devices

class IOPorts:
    def __init__(self, device = [0x20, 0x21]):
        #print("IOPorts init ", device)
        pass
     
    def set(self, board_id, output_id):
        #print("IOPorts set", board_id, output_id)
        pass
      
    def clear(self, board_id, output_id):
        #print("IOPorts clear", board_id, output_id)
        pass
        