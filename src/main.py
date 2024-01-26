import time
from logger import *
import login

from vrm import *
from vrm_status import *

from load_manager import *


if __name__ == "__main__":
    error_logger = Logger("logs/error.log")
    state_logger = Logger("logs/state.log")
    power_logger = Logger("logs/power.log") 

    charge_on   = 90.0
    charge_off  = 80.0
    
    #maximum power from grid to turn off
    total_ip_max = 500.0

    #time step, in seconds
    dt = 10

    load_manager = LoadManager(6)

    while True:
        load_manager.remove_all()
        time.sleep(dt)

        instalation_id = login.instalation_id
        vrm_api = VRM_API(username=login.username, password=login.password)

        if vrm_api._initialized != True:
            error_logger.add("API not initialized")
            continue

        vrm_status = VRMStatus(vrm_api, instalation_id)

        if vrm_status.api_ready != True:
            error_logger.add("API not ready")
            continue  
            
        error_logger.add("API ready")

        #main loop
        while True:
            time_start = time.time()

            result = vrm_status.get_battery_state()
            if result is None:
                error_logger.add("battery state reading error")
                break

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
                break

            print("mppt")
            print(mppt_power)
            print("\n\n")


            result = vrm_status.get_inverter_state()
            if result is None:
                error_logger.add("inverter state reading error")
                break

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
            
            
            #too low battery
            if charge < charge_off:
                load_manager.remove_all()

            #too much power from grid, remove one load
            elif total_ip > total_ip_max:
                load_manager.remove_load()

            #turn new device on
            elif charge > charge_on:
                load_manager.add_load()

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
                state_log+= load_manager.get_state()
                state_log+= "\n"

                state_log+= "\n"
                state_logger.add(state_log)


            time_stop = time.time()

            duration = time_stop - time_start

            print("reading time = ", duration, "\n\n")

            required_sleep = dt - duration
            if required_sleep < 0.1:
                required_sleep = 0.1

            time.sleep(required_sleep)
