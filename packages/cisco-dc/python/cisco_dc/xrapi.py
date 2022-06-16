from scrapli.driver.core import IOSXRDriver
from . import utils
import logging


class Xrapi:

    def __init__(self, host, username, password, log):
        self.log = log
        self.r1 = {
            "host": host,
            "auth_username": username,
            "auth_password": password,
            "auth_strict_key": False,
            "timeout_socket": 5,  # timeout for establishing socket/initial connection
            "timeout_transport": 10,  # timeout for ssh|telnet transport
        }
        logging.getLogger('scrapy').propagate = False

    def send_show_commands(self, bd, cmd_dict):
        """Function to run precheck commands on DCI and raise exception if necessary

        Args:
            bd: Service node
            cmd_dict: Default dict object
        """
        with IOSXRDriver(**self.r1) as ssh:
            if cmd_dict.get('vrf'):
                cmd_list = cmd_dict.get('vrf')
                reply = ssh.send_commands(cmd_list)
                for r in reply:
                    vrf = utils.get_vrf_from_dci_router(bd, r)

                cmd_dict = utils.update_command_dict(bd, vrf, cmd_dict)
                for prefix, cmd_list in cmd_dict.items():
                    reply = ssh.send_commands(cmd_list)
                    for r in reply:
                        utils.is_prefix_used(prefix, r, self.log)
