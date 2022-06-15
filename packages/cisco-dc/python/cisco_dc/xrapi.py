from scrapli.driver.core import IOSXRDriver
from scrapli.exceptions import ScrapliException


class Xrapi:

    def __init__(self, host, username, password, log):
        self.log = log
        r1 = {
            "host": host,
            "auth_username": username,
            "auth_password": password,
            "auth_strict_key": False,
            "timeout_socket": 5,  # timeout for establishing socket/initial connection
            "timeout_transport": 10,  # timeout for ssh|telnet transport
        }

    def send_show_commands(self, cmd_list, log):
        try:
            with IOSXRDriver(**self.r1) as ssh:
                reply = ssh.send_commands(cmd_list)

                for r in reply:
                    log.info(r.result)

        except ScrapliException as error:
            print(error, self.r1["host"])
