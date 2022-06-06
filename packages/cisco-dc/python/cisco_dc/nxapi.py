import urllib3
import requests
import json


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Nxapi:

    def __init__(self, switch, username, password, log):
        self.switch = switch
        self.auth = (username, password)
        self.log = log
        self.headers={'content-type':'application/json-rpc'}
        self.url = f'http://{self.switch}/ins'

    def get_interfaces_status(self):
        try:
            rsp = requests.post(url=self.url, verify=False)

        except Exception as e:
            self.log.error(e)
            raise

        else:
            return rsp.json()
