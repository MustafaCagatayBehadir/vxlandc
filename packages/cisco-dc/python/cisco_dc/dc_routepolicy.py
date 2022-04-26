import ncs
import _ncs
import ncs.maapi as maapi
import ncs.maagic as maagic
from ipaddress import ip_address, IPv4Address, IPv6Address

from . import utils


class RoutePolicyConfigService(ncs.application.Service):

    @ncs.application.Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        _configure_dc_route_policy(root, service, tctx, self.log)


def _configure_dc_route_policy(root, dc_rpl, tctx, log):
    """Function to configure port service

    Args:
        root: Maagic object pointing to the root of the CDB
        dc_rpl: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    _set_hidden_leaves(root, dc_rpl, log)
    _apply_template(service)


def _set_hidden_leaves(root, dc_rpl, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        dc_rpl: service node
        log: log object (self.log)

    """
    for match_rule in dc_rpl.rules_set.match_rules:
        log.info('Match Rule Name :', match_rule.name)
        if match_rule.match_type == 'prefix-list':
            for route_destination_ip in match_rule.route_destination_ip:
                ip = utils.getIpAddress(route_destination_ip.ip)
                if not match_rule.address_family and type(ip_address(ip)) is IPv4Address:
                    match_rule.address_family = 'ipv4'
                elif not match_rule.address_family and type(ip_address(ip)) is IPv6Address:
                    match_rule.address_family = 'ipv6'
                elif match_rule.address_family.string == 'ipv4' and type(ip_address(ip)) is IPv4Address:
                    continue
                elif match_rule.address_family.string == 'ipv6' and type(ip_address(ip)) is IPv6Address:
                    continue
                else:
                    raise Exception(
                        f'Prefix-list {match_rule.name} should not contain both ipv4 and ipv6 addresses.')

    for route_policy in dc_rpl.route_policy:
        log.info('Route Policy Name :', route_policy.profile)
        for match_and_set_group in route_policy.match_and_set_group:
            for rpl_match_rule in match_and_set_group.match_rules:
                match_rule = dc_rpl.rules_set.match_rules[rpl_match_rule.name]
                if not route_policy.address_family and match_rule.address_family.string == 'ipv4':
                    route_policy.address_family = 'ipv4'
                elif not route_policy.address_family and match_rule.address_family.string == 'ipv6':
                    route_policy.address_family = 'ipv6'
                elif route_policy.address_family.string == 'ipv4' and match_rule.address_family.string == 'ipv4':
                    continue
                elif route_policy.address_family.string == 'ipv6' and match_rule.address_family.string == 'ipv6':
                    continue
                else:
                    raise Exception(
                        f'Route-Policy {route_policy.name} should not contain both ipv4 and ipv6 prefix-lists.')                  

def _apply_template(dc_rpl):
    """Function to apply configurations to devices

    Args:
        dc_rpl: service node

    """
    template = ncs.template.Template(dc_rpl)
    template.apply('cisco-dc-services-fabric-routepolicy')
