from scrapli.driver.core import IOSXRDriver
from scrapli.exceptions import ScrapliException


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

    def send_show_commands(self, cmd_dict):
        try:
            with IOSXRDriver(**self.r1) as ssh:
                self.log.info('Command List: ', cmd_dict)
                if 'vrf' in cmd_dict and cmd_dict['vrf']:
                    reply = ssh.send_commands(cmd_dict['vrf'])
                    for r in reply:
                        self.log.info(r.result)
                # Delete vrf key after run the command
                cmd_dict.pop('vrf')
                for prefix, cmd_list in cmd_dict.items():
                    reply = ssh.send_commands(cmd_list)
                    for r in reply:
                        self.log.info(r.result)

        except ScrapliException as error:
            print(error, self.r1["host"])
