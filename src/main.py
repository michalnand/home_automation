import time
import libs

import login

from datetime import datetime

if __name__ == "__main__":

    logs_prefix =  str(datetime.utcfromtimestamp(time.time()))
    logs_prefix = logs_prefix.replace("'", "")
    logs_prefix = logs_prefix.replace(" ", "_")

    print(logs_prefix)

    logs_prefix = "logs/" + logs_prefix

    error_logger = libs.Logger(logs_prefix, "/error.log")
    state_logger = libs.Logger(logs_prefix, "/state.log")
    power_logger = libs.Logger(logs_prefix, "/power.log") 
    load_logger  = libs.Logger(logs_prefix, "/load.log") 

    #baterry status when turn on    
    charge_on   = 92.0 

    #baterry status when turn off
    charge_off  = 90.0
    
    #maximum power from grid to turn off
    total_ip_max = 600.0
 
    #time step, in seconds
    dt = 10

    load_manager = libs.LoadManager()

    load_manager.led_on(0)
    load_manager.led_on(1)
    load_manager.remove_all()

    readings_repetitions = 0

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
        vrm_api = libs.VRM_API(username=login.username, password=login.password)

        if vrm_api._initialized != True:
            load_manager.remove_all()
            error_logger.add("API not initialized")
            readings_repetitions+= 1
            continue

        vrm_status = libs.VRMStatus(vrm_api, instalation_id)

        if vrm_status.api_ready != True:
            load_manager.remove_all()
            error_logger.add("API not ready")
            readings_repetitions+= 1
            continue

        result = vrm_status.get_battery_state()
        if result is None:
            error_logger.add("battery state reading error")
            readings_repetitions+= 1
            continue

        voltage, current, charge = result

        print("battery")
        print("voltage = " + str(voltage) + "V")
        print("current = " + str(current) + "A")
        print("charge  = " + str(charge) +  "%")
        print("\n\n\n")


        mppt_power = []
        for instance in vrm_status.devices["Solar Charger"]:
            result = vrm_status.get_mppt_state(instance)
            mppt_power.append(result)

        if None in mppt_power:
            error_logger.add("mppt state reading error")
            readings_repetitions+= 1
            continue

        print("mppt")
        print(mppt_power)
        print("\n\n")


        result = vrm_status.get_inverter_state()
        if result is None:
            error_logger.add("inverter state reading error")
            readings_repetitions+= 1
            continue

        ip1, op1, ip2, op2, ip3, op3 = result

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

        power_logger.add(power_log)
        
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


