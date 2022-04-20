import _ncs
import ncs.maapi as maapi
import ncs.maagic as maagic
from ipaddress import ip_address, IPv4Address, IPv6Address

from . import utils


class RoutePolicyConfigServiceValidator(object):
    def __init__(self, log):
        self.log = log

    def cb_validate(self, tctx, kp, newval):
        '''
        Validating dc-route-policy match-rules prefix-lists are not mixed with ipv4 unicast and ipv6 unicast
        '''
        try:
            self.log.debug("Validating dc-routepolicy service")
            m = maapi.Maapi()
            th = m.attach(tctx)

            service = maagic.get_node(th, str(kp))

            # raise Exception("IP version overlap config")
            self._no_ip_version_overlap_validation(th, service)

        except Exception as e:
            self.log.error(e)
            raise
        return _ncs.OK

    def _no_ip_version_overlap_validation(self, th, dc_route_policy):
        '''
        :th: ncs.maapi.Transaction
        :rpl: ncs.maagic.ListElement
        :fabric: fabric name string
        '''
        for match_rule in dc_route_policy.rules_set.match_rules:
            if match_rule.match_type == 'prefix-list':
                self.log.info('Match rule name :', match_rule.name)
                self._check_no_ip_version_overlap(th, match_rule)

    def _check_no_ip_version_overlap(self, th, match_rule):
        '''
        :th: ncs.maapi.Transaction
        :match_rule: ncs.maagic.List
        '''
        flag_ipv4, flag_ipv6 = False, False
        route_destination_ip = match_rule.route_destination_ip
        for prefix in route_destination_ip:
            self.log.info('Prefix :', prefix.ip)
            ip = utils.getIpAddress(prefix.ip)
            if type(ip_address(ip)) is IPv4Address:
                flag_ipv4 = True
                self.log.info(f'{ip} is an IPv4 address')
            elif type(ip_address(ip)) is IPv6Address:
                flag_ipv6 = True
                self.log.info(f'{ip} is an IPv6 address')

            if flag_ipv4 and flag_ipv6:
                raise Exception(
                    f'Prefix-list {match_rule.name} should not contain both ipv4 and ipv6 addresses.')
