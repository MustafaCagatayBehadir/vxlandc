import logging
import requests
import json

logger = logging.getLogger(__name__)


class NsoRestconfCall:
    """
    A Class used to deal with NSO northbound RESTCONF api calls
    """

    def __init__(self, ip="127.0.0.1", port="8080", user="admin", pwd="admin"):
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
        url = f"http://{self.ip}:{self.port}/restconf/data/{path}"
        header = {
            "Content-type": "application/yang-data+json",
            "Accept": "application/yang-data+json",
        }
        resp = requests.get(url, headers=header, auth=self.auth)
        logger.debug(json.dumps(resp.json(), sort_keys=True, indent=4))
        return resp
