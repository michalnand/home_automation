import libs
import time

if __name__ == "__main__":
    load_manager = libs.LoadManager()

    state = 0
    load_count = 0

    while True:
        load_manager.led_on(0)
        load_manager.led_on(1)

        time.sleep(1)

        load_manager.led_off(0)
        load_manager.led_off(1)


        time.sleep(1)

        print("step ", load_manager.get_log())

        if state == 0:
            load_manager.add_load()
            load_count+= 1

            if load_count > 10:
                load_manager.remove_all()
                load_count = 0
                state = 1
                
        elif state == 1:
            load_manager.add_load()
            load_count+= 1

            if load_count > 10:
                state = 2

        elif state == 2:
            load_manager.remove_load()
            load_count-= 1

            if load_count <= 0:
                state = 0
             



        

