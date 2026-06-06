
import requests
import json

class VRMAPI:


    def __init__(self, instalation_id, token):
        self.instalation_id = instalation_id
        self.token = token


   
    def get(self):
        raw_data = self._get_raw_data()

        #self._print_raw_data(raw_data)

        if raw_data is None:
            return None, -1
        
        parsed_data = self._parse_data(raw_data)

        if parsed_data is None:
            return None, -2
        
        if self._check_all_leaves_not_none(parsed_data) == False:
            return None, -3
        
        return parsed_data, 0

    def _print_raw_data(self, raw_data):
        if "records" in raw_data:
            for record in raw_data["records"]:
                device = record.get("Device", "")
                desc = record.get("description", "")
                val = record.get("formattedValue") 
                
                print(device, " : ", desc, " : ", val)


    
    def _get_raw_data(self):
        # 2. Add it to your request headers instead of doing a login request
        headers = {
            'X-Authorization': self.token,
            'Content-Type': 'application/json'
        }

        # Example of making a data request using the token header
        # (Replace with your actual endpoint, like getting installation details)
        INSTALLATION_ID = self.instalation_id  # Your VRM Site ID
        DATA_ENDPOINT = f"https://vrmapi.victronenergy.com/v2/installations/{INSTALLATION_ID}/diagnostics"

        try:
            result = requests.get(DATA_ENDPOINT, headers=headers)
            if result.status_code == 200:
                data = result.json()
                return data
            else:
                return None
            
        except Exception as e:
            print(f"Connection failed: {e}") 
            return None
    


    def _parse_data(self, vrm_json):
        result = {
            "battery": {},
            "mppts": [],
            "inverters": []
        }

        mppt_initial = {"id" : None, "voltage" : None, "current" : None, "power" : None}
        mppt_curr    = dict(mppt_initial)

        inverter_initial = {"p_in" : None, "u_in" : None, "i_in" : None, "f_in" : None, "p_out" : None, "u_out" : None, "i_out" : None}

        for n in range(3):  
            result["inverters"].append(dict(inverter_initial))

        try:
            if "records" in vrm_json:
                for record in vrm_json["records"]:
                    device = record.get("Device", "")
                    desc = record.get("description", "")
                    val = record.get("formattedValue")  # Human-readable string like "236.7 V" or "25 %"
                    
                    val = str(val)
                    if device == "Battery Monitor":
                        if desc == "Voltage":
                            result["battery"]["voltage"] = self._valid_range(float(val.split()[0]), 0, 100)
                        elif desc == "Current":
                            result["battery"]["current"] = self._valid_range(float(val.split()[0]), -500, 500)
                        elif desc == "Battery temperature":
                            result["battery"]["temperature"] = self._valid_range(float(val.split()[0]), -100, 100)
                        elif desc == "State of charge":
                            result["battery"]["soc"] = self._valid_range(float(val.split()[0]), -110, 110)
                        elif desc == "State of health":
                            result["battery"]["soh"] = self._valid_range(float(val.split()[0]), -110, 110)

                    if device == "Solar Charger":
                        if "Solar charger serial number" in desc:
                            mppt_curr = dict(mppt_initial)
                            mppt_curr["id"] = str(val)

                        elif desc == "Voltage":
                            mppt_curr["voltage"] = self._valid_range(float(val.split()[0]), -1000000, 1000000)

                        elif desc == "Current":
                            mppt_curr["current"] = self._valid_range(float(val.split()[0]), -1000000, 1000000)

                        elif desc == "PV power":
                            mppt_curr["power"] = self._valid_range(float(val.split()[0]), -1000000, 1000000)

                        elif desc == "Error code":
                            mppt_curr["error_code"] = str(val)

                            result["mppts"].append(mppt_curr)
                            mppt_curr = dict(mppt_initial)

                    if device == "VE.Bus System":

                        for n in range(3):
                            if desc == "Input voltage phase " + str(n+1):
                                result["inverters"][n]["u_in"] = self._valid_range(float(val.split()[0]),  -1000000, 1000000)
                            elif desc == "Output voltage phase " + str(n+1):
                                result["inverters"][n]["u_out"] = self._valid_range(float(val.split()[0]),  -1000000, 1000000)
                            elif desc == "Input current phase " + str(n+1):
                                result["inverters"][n]["i_in"] = self._valid_range(float(val.split()[0]),  -1000000, 1000000)
                            elif desc == "Output current phase " + str(n+1):
                                result["inverters"][n]["i_out"] = self._valid_range(float(val.split()[0]),  -1000000, 1000000)
                            elif desc == "Input power " + str(n+1):
                                result["inverters"][n]["p_in"] = self._valid_range(float(val.split()[0]),  -1000000, 1000000)
                            elif desc == "Output power " + str(n+1):
                                result["inverters"][n]["p_out"] = self._valid_range(float(val.split()[0]),  -1000000, 1000000)
                            elif desc == "Input frequency " + str(n+1):
                                result["inverters"][n]["f_in"] = self._valid_range(float(val.split()[0]),  -1000000, 1000000)

                return result
            else:
                return None
                 
        except Exception as e:
            print(f"Parsing failed: {e}") 
            return None
    

    def _valid_range(self, x, min_x, max_x):

        if isinstance(x, float) == False:
            return None
        
        if x < min_x:
            return None
        
        if x > max_x:
            return None
        
        return x
    

    def _check_all_leaves_not_none(self, data) -> bool:
        """Recursively checks if every leaf node in a JSON-like structure is NOT None.
        
        Returns True if all leaves are not None, and False if any None is found.
        """
        # Case 1: If the current node is a dictionary, check all its values
        if isinstance(data, dict):
            return all(self._check_all_leaves_not_none(value) for value in data.values())
        
        # Case 2: If the current node is a list, check all its elements
        elif isinstance(data, list):
            return all(self._check_all_leaves_not_none(item) for item in data)
        
        # Case 3: We hit a leaf node. Return True if it's not None, False if it is.
        else:
            return data is not None
            
            