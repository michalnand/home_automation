import pathlib 
import time

from datetime import datetime


class Logger:

    def __init__(self, name):

        path = pathlib.Path().absolute()

        self.f_name = str(path) + "/" + name

        f = open(self.f_name , "w")
        f.close()
    
    def add(self, value):
        
        t = time.time()

        result = "" 
        result+= str(datetime.utcfromtimestamp(t)) + " "
        result+= str(t) + " "
        result+= str(value) + "\n"

        f = open(self.f_name , "a")
        f.write(result)
        f.close()

     