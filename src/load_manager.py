class LoadManager:

    def __init__(self, loads_count):
        print("LoadManager : init")

        self.loads_count  = loads_count
        self.load_level   = 0
        self.is_change    = True

        self.remove_all()

    def remove_all(self):
        if self.load_level != 0:
            self.is_change    = True

        self.load_level   = 0

        print("LoadManager : remove_all ", self.load_level)

    def remove_load(self):
        if self.load_level > 0:
            self.load_level-= 1
            self.is_change    = True

        print("LoadManager : remove_load ", self.load_level)

    def add_load(self):
        if self.load_level < self.loads_count:
            self.load_level+= 1
            self.is_change    = True

        print("LoadManager : add_load ", self.load_level)


    def change(self):
        result = self.is_change
        self.is_change = False

        return result
    
    def get_state(self):
        return "loads_count = " + str(self.load_level)