import os
import pathlib 
import time

from datetime import datetime


class Logger:

    def __init__(self, prefix, name):

        path = os.path.join(pathlib.Path().absolute(), pathlib.Path(prefix))

        print("creating path ", path)

        exist = os.path.exists(path)
        if not exist:
            os.makedirs(path)

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

     