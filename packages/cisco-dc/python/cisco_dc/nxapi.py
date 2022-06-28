import urllib3
import requests
import json


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Nxapi:

    def __init__(self, switch, username, password, log):
        self.switch = switch
        self.auth = (username, password)
        self.log = log
        self.headers = {'content-type': 'application/json-rpc'}
        self.url = f'https://{self.switch}/ins'

    def send_show_command(self, cmd):
        try:
            payload = [
                {
                    "jsonrpc": "2.0",
                    "method": "cli",
                    "params": {
                        "cmd": cmd,
                        "version": 1
                    },
                    "id": 1
                }
            ]
            rsp = requests.post(
                url=self.url, data=json.dumps(payload), headers=self.headers, auth=self.auth, verify=False)
        except Exception as e:
            self.log.error(e)
            raise
        else:
            return rsp.json()
