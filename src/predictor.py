import time
from datetime import datetime, timezone
from suntime import Sun, SunTimeException

class Predictor:


    def __init__(self, lat, lon):


        warsaw_lat = 51.21
        warsaw_lon = 21.01

        sun = Sun(warsaw_lat, warsaw_lon)

        #current_time = datetime.utcfromtimestamp(time.time())
        current_time = datetime.now(timezone.utc)

        print(time.tzname)

        today_sunset = sun.get_sunset_time()

        print(current_time)
        print(today_sunset)

        time_to_sunset = self._split_time(today_sunset.time()) - self._split_time(current_time.time())

        print(">>> ", time_to_sunset, time_to_sunset/3600.0)
    

    def _split_time(self, x):
        tmp = str(x).split(':')
        
        h = int(tmp[0])
        m = int(tmp[1])
        s = float(tmp[2])

        t = 3600*h + 60*m + s
        return t


if __name__ == "__main__":
    p = Predictor(0, 0)