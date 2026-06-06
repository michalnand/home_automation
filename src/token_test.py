import requests
import login
import json

import libs

if __name__ == "__main__":

    api = libs.VRMAPI(login.instalation_id, login.token)

    json_res, error_code = api.get()

    print("\n\n")
    print("error_code ", error_code)
    print(json.dumps(json_res, indent=2))
