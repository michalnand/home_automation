

class VRMStatus:

    def __init__(self, vrm_api, instalation_id):
        self.vrm_api        = vrm_api
        self.instalation_id = instalation_id

        self.overview       = vrm_api.get_overview(instalation_id)

        if self.overview is not None:
            self.api_ready = True
            self.devices = self._get_devices(self.overview)
        else:
            self.api_ready = False
            self.devices = []

    def _get_devices(self, overview_resp):
        devices = {}
        for d in overview_resp["records"]["devices"]:

            if "name" in d:
                name = d["name"]
            else:
                name = -1

            if "instance" in d:
                instance = d["instance"]
            else:
                instance = -1

            if name not in devices:
                devices[name]=[]

            devices[name].append(instance)
            
        return devices
    

    def get_battery_state(self):

        try:
            result  = self.vrm_api.battery_summary_widget(self.instalation_id, instance=self.devices["Battery Monitor"])

            voltage = result["records"]["data"]["47"]["rawValue"]
            current = result["records"]["data"]["49"]["rawValue"]
            charge  = result["records"]["data"]["51"]["rawValue"]


            return float(voltage), float(current), float(charge)
        except Exception:
            return None

    def get_mppt_state(self, instance):
        try:
            resp = self.vrm_api.solar_charger_summary_widget(self.instalation_id, instance)

            power = resp["records"]["data"]["107"]["valueFloat"]  # Battery watts
            #voltage = resp["records"]["data"]["81"]["valueFloat"]  # Voltage
            
            #stats  = self.vrm_api.graph_widgets(self.instalation_id, measurement_codes = ["ScW"], instance=instance)
            #power  = stats["records"]["data"]["107"][-1][1]
        
            return float(power)
        except Exception:
            return None


    
    def get_inverter_state(self):
        try:
            '''
            stats  = self.vrm_api.graph_widgets(self.instalation_id, measurement_codes = ["IP1", "OP1", "IP2", "OP2", "IP3", "OP3"])

            print("inverter state")
            print(stats)

            ip1 = float(stats["records"]["data"]["17"][-1][1])
            op1 = float(stats["records"]["data"]["29"][-1][1])
            ip2 = float(stats["records"]["data"]["18"][-1][1])
            op2 = float(stats["records"]["data"]["30"][-1][1])
            ip3 = float(stats["records"]["data"]["19"][-1][1])
            op3 = float(stats["records"]["data"]["31"][-1][1])
            '''

            result = self.vrm_api.status_widget(self.instalation_id)
        
            # Print raw to inspect attribute IDs
            # print(json.dumps(result, indent=2))
            
            data = result["records"]["data"]
            
            # These IDs can vary per site, but typically:
            # - 17: Input power (L1)
            # - 29: Output power (L1)
            # - 18: Input power (L2)
            # - 30: Output power (L2)
            # - 19: Input power (L3)
            # - 31: Output power (L3)
            
            ip1 = data["17"]["valueFloat"]
            op1 = data["29"]["valueFloat"]
            ip2 = data["18"]["valueFloat"]
            op2 = data["30"]["valueFloat"]
            ip3 = data["19"]["valueFloat"]
            op3 = data["31"]["valueFloat"]


            return ip1, op1, ip2, op2, ip3, op3
        except Exception:
            print("exception")
            print(Exception)
            return None
   