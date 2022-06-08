from scrapli.driver.core import IOSXRDriver
from scrapli.exceptions import ScrapliException


r1 = {
    "host": "10.211.48.52",
    "auth_username": "dcnm_nso_test",
    "auth_password": "dcnm_nso_test",
    "auth_strict_key": False,
    "timeout_socket": 5,  # timeout for establishing socket/initial connection
    "timeout_transport": 10,  # timeout for ssh|telnet transport
}


def send_show(show_command):
    try:
        with IOSXRDriver(**r1) as ssh:
            reply = ssh.send_command(show_command)
            return reply.textfsm_parse_output() if reply.textfsm_parse_output() else reply.result
    except ScrapliException as error:
        print(error, r1["host"])
