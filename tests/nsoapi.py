import logging
import requests
import json


logfile = 'logs/nsoapi.log'
logging.basicConfig(filename=logfile, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class NsoRestconfCall:
    """
    A Class used to deal with NSO northbound RESTCONF api calls
    """

    def __init__(self, ip="10.211.101.208", port="8888", user="admin", pwd="Tellcom123!"):
        """
        Args:
            ip (str): IP address of the NSO (default is localhost)
            port (str): the port for connecting NSO restconf
            user (str): username to log into the NSO
            pwd (str): password to log into the NSO
        """
        self.ip = ip
        self.port = port
        self.auth = (user, pwd)

    def get(self, path):
        """Query the info a certain NSO path
        Args:
            path (str): the path to the NSO resource
        Returns:
            resp (requests return obj):
        """
        url = f"https://{self.ip}:{self.port}/restconf/data/{path}"
        header = {
            "Content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json",
        }
        resp = requests.get(url, headers=header, auth=self.auth, verify=False)
        return resp

    def patch(self, payload, path, params):
        """Send the data that we want to store
        Args:
            payload (str or Path): the path to the payload
            path (str): the path to the NSO resource
            params (str): the query parameter
        Returns:
            resp (requests return obj):
        """
        url = (
            f"https://{self.ip}:{self.port}/restconf/data/{path}?{params}"
            if params
            else f"https://{self.ip}:{self.port}/restconf/data/{path}"
        )
        header = {
            "content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json",
        }
        with open(payload) as json_file:
            json_data = json.load(json_file)
        resp = requests.patch(
            url, data=json.dumps(json_data), headers=header, auth=self.auth, verify=False
        )
        return resp

    def put(self, payload, path, params):
        """Send the data that we want to store
        Args:
            payload (str or Path): the path to the payload
            path (str): the path to the NSO resource
            params (str): the query parameter
        Returns:
            resp (requests return obj):
        """
        url = (
            f"https://{self.ip}:{self.port}/restconf/data/{path}?{params}"
            if params
            else f"https://{self.ip}:{self.port}/restconf/data/{path}"
        )
        header = {
            "content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json",
        }
        with open(payload) as json_file:
            json_data = json.load(json_file)
        resp = requests.put(
            url, data=json.dumps(json_data), headers=header, auth=self.auth, verify=False
        )
        return resp

    def post(self, payload, path, params, action):
        """Send the data that we want to store
        Args:
            payload (str or Path): the path to the payload
            path (str): the path to the NSO resource
            params (str): the query parameter
            action (boolean): set true if action
        Returns:
            resp (requests return obj):
        """
        restconf_root = "restconf/data" if not action else "restconf/operations"
        url = (
            f"https://{self.ip}:{self.port}/{restconf_root}/{path}?{params}"
            if params
            else f"https://{self.ip}:{self.port}/{restconf_root}/{path}"
        )
        header = {
            "content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json",
        }
        with open(payload) as json_file:
            json_data = json.load(json_file)
        resp = requests.post(
            url, data=json.dumps(json_data), headers=header, auth=self.auth, verify=False
        )
        return resp

    def delete(self, path):
        """Delete the instance of a certain NSO path
        Args:
            path (str): the path to the NSO resource
        Returns:
            resp (requests return obj):
        """

        url = f"https://{self.ip}:{self.port}/restconf/data/{path}"
        resp = requests.delete(url, auth=self.auth, verify=False)
        return resp
