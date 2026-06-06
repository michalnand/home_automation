import time
import libs

import login

from vrm_api import *

from datetime import datetime


if __name__ == "__main__":

    '''
        i2c0 : 
            add for enable :
                sudo nano /boot/firmaware/config.txt
                dtparam=i2c_vc=on
                reboot
            check : 
                sudo i2cdetect -l

            pins: 
                GPIO0 : sda, num 27
                GPIO1 : scl, num 28
    '''
    i2c_bus = 0 

    #logs_prefix =  str(datetime.utcfromtimestamp(time.time()))
    logs_prefix = datetime.fromtimestamp(time.time()).astimezone()
    logs_prefix = str(logs_prefix)

    logs_prefix = logs_prefix.replace("'", "")
    logs_prefix = logs_prefix.replace(" ", "_")


    logs_prefix = "logs/" + logs_prefix

    error_logger = libs.Logger(logs_prefix, "/error.log")
    state_logger = libs.Logger(logs_prefix, "/state.log")
    power_logger = libs.Logger(logs_prefix, "/power.log") 
    load_logger  = libs.Logger(logs_prefix, "/load.log") 

    history_logger = libs.HistoryLogger("logs/history.log", 60480)

    #baterry status when turn on    
    charge_on   = 90.0 

    #baterry status when turn off
    charge_off  = 87.0
    
    #maximum power from grid to turn off
    total_ip_max = 600.0
 
    #time step, in seconds
    dt = 10

    # check devices I2C connection

    '''
    while True:
        active_devices, errors = libs.check_devices(1)
        active_devices, errors = libs.check_devices(i2c_bus)
        time.sleep(0.2)
    '''

    active_devices, errors = libs.check_devices(i2c_bus)

    if len(errors) != 0:
        for e in errors:
            error_logger.add(e)
        
        error_logger.add("exiting")
        exit(1)

    load_manager = libs.LoadManager(i2c_bus)

    load_manager.led_on(0)
    load_manager.led_on(1)
    load_manager.remove_all()

    readings_repetitions = 0

    samples_cnt = 0

    #main loop
    while True:
        

        #too many tries, exiting
        if readings_repetitions > 10:
            load_manager.remove_all()
            error_logger.add("too many readings repetitions")
            error_logger.add("exiting")
            exit(1)

        time_start = time.time()
        
        while time.time() < time_start + dt:
            print("waiting")
            load_manager.led_on(0)
            load_manager.led_on(1)
            time.sleep(0.2)
            
            load_manager.led_off(0)
            load_manager.led_off(1)
            time.sleep(0.8)

        
        instalation_id = login.instalation_id
       
        vrm_api = VRMAPI(login.instalation_id, login.token)

      
        vrm_status, error_code = vrm_api.get()

        if error_code != 0:
            load_manager.remove_all()
            error_logger.add("API not ready, error code " + str(error_code))
            readings_repetitions+= 1
            continue

        samples_cnt+= 1
        
        voltage = vrm_status["battery"]["voltage"]
        current = vrm_status["battery"]["current"]
        charge  = vrm_status["battery"]["soc"]
        health  = vrm_status["battery"]["soh"]

        print("battery")
        print("voltage = " + str(voltage) + "V")
        print("current = " + str(current) + "A")
        print("charge  = " + str(charge) +  "%")
        print("health  = " + str(health) +  "%")
        print("\n\n\n")


        mppt_power = []
        for mppt in vrm_status["mppts"]:
            mppt_power.append(mppt["power"])


        print("mppt")
        print(mppt_power)
        print("\n\n")


        ip1 = vrm_status["inverters"][0]["p_in"]
        op1 = vrm_status["inverters"][0]["p_out"]
        
        ip2 = vrm_status["inverters"][1]["p_in"]
        op2 = vrm_status["inverters"][1]["p_out"]
        
        ip3 = vrm_status["inverters"][2]["p_in"]
        op3 = vrm_status["inverters"][2]["p_out"]


        total_ip = ip1 + ip2 + ip3
        total_op = op1 + op2 + op3

        print("inverter input/output power")
        print("L1 = ", ip1, op1, "W")
        print("L2 = ", ip2, op2, "W")
        print("L3 = ", ip3, op3, "W")
        print("total = ", total_ip, total_op, "W")
        print("\n\n")

        power_log = ""
        power_log+= str(voltage) + " "
        power_log+= str(current) + " "
        power_log+= str(charge)  + " "

        for p in mppt_power:
            power_log+= str(p) + " "
        power_log+= " " 

        power_log+= str(total_ip) + " "
        power_log+= str(total_op) + " "

        
        
        load_logger_str = ""

        #clear reafings counter, since we readed everything
        readings_repetitions = 0

        
        #too low battery
        if charge <= charge_off:
            load_manager.remove_all()
            load_logger_str+= "remove_all : charge < charge_off " + load_manager.get_log()

        #too much power from grid, remove one load
        elif total_ip >= total_ip_max:
            load_manager.remove_load()
            load_logger_str+= "remove_load : total_ip > total_ip_max " + load_manager.get_log()

        #turn new device on
        elif charge >= charge_on:
            load_manager.add_load()
            load_logger_str+= "add_load : charge > charge_on " + load_manager.get_log()

        #log status
        if load_manager.change():
            power_logger.add(power_log)

            state_log = "\n"
            state_log+= "battery\n"
            state_log+= "voltage " + str(voltage) + " V" + "\n"
            state_log+= "current " + str(current) + " A" + "\n"
            state_log+= "charge "  + str(charge) +  " %" + "\n"
            state_log+= "\n"

            state_log+= "mppt\n"
            state_log+= "power " + str(mppt_power) + " W" + "\n"
            state_log+= "\n"

            state_log+= "inverter\n"
            state_log+= "L1 = " + str(ip1) + " " + str(op1) + " W\n"
            state_log+= "L2 = " + str(ip2) + " " + str(op2) + " W\n"
            state_log+= "L3 = " + str(ip3) + " " + str(op3) + " W\n"
            state_log+= "\n"


            state_log+= "load_manager\n"
            state_log+= load_manager.get_log() + "\n"
            state_log+= "\n"

            state_log+= "\n"
            state_logger.add(state_log)

            load_logger.add(load_logger_str)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if (samples_cnt%10) == 0:
            vrm_status["relay_state"] = load_manager.is_on()
            history_logger.update(vrm_status)


