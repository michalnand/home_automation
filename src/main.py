from vrm import *
from vrm_status import *
import numpy

import login


instalation_id = login.instalation_id
vrm_api = VRM_API(username=login.username, password=login.password)
vrm_status = VRMStatus(vrm_api, instalation_id)

voltage, current, charge = vrm_status.get_battery_state()


print("battery")
print("voltage = ", voltage, "V")
print("current = ", current, "A")
print("charge  = ", charge,  "%")
print("\n\n\n")


print("MPPT power")
for instance in vrm_status.devices["Solar Charger"]:
    power = vrm_status.get_mppt_state(instance)
    print("id = ", instance, " power = ", power, "W")
print("\n\n")


ip1, op1, ip2, op2, ip3, op3 = vrm_status.get_inverter_state()

print("inverter input/output power")
print("L1 = ", ip1, op1, "W")
print("L2 = ", ip2, op2, "W")
print("L3 = ", ip3, op3, "W")



op = numpy.array([op1, op2, op3])
ip = numpy.array([ip1, ip2, ip3])

min_idx = numpy.argmin(op)

print("\n\n")

if charge > 90 and op[min_idx] < 150 and ip[min_idx] < 50:
    print("relay on for L", min_idx+1)
else:
    print("relay off")
