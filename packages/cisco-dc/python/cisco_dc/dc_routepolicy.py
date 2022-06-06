import ncs
from ipaddress import ip_address, IPv4Address, IPv6Address

from . import utils


class RoutePolicyConfigService(ncs.application.Service):

    @ncs.application.Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        _configure_dc_route_policy(root, service, tctx, self.log)
        _apply_template(service)


def _configure_dc_route_policy(root, dc_rpl, tctx, log):
    """Function to configure port service

    Args:
        root: Maagic object pointing to the root of the CDB
        dc_rpl: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    _set_hidden_leaves(root, dc_rpl, log)


def _set_hidden_leaves(root, dc_rpl, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        dc_rpl: service node
        log: log object (self.log)

    """
    for match_rule in dc_rpl.rules_set.match_rules:
        if match_rule.match_type == 'prefix-list':
            for prefix in match_rule.prefix:
                ip = utils.getIpAddress(prefix.ip)
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

    for set_rule in dc_rpl.rules_set.set_rules:
        if set_rule.nh_address:
            ip = set_rule.nh_address
            set_rule.address_family = 'ipv4' if type(
                ip_address(ip)) is IPv4Address else 'ipv6'

    for route_policy in dc_rpl.route_policy:
        for match_and_set_group in route_policy.match_and_set_group:
            for rpl_match_rule in match_and_set_group.match_rules:
                match_rule = dc_rpl.rules_set.match_rules[rpl_match_rule.name]
                if match_rule.match_type == 'prefix-list':
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
                            f'Route-Policy {route_policy.profile} should not contain both ipv4 and ipv6 prefix-lists.')

        for match_and_set_group in route_policy.match_and_set_group:
            for rpl_set_rule in match_and_set_group.set_rules:
                set_rule = dc_rpl.rules_set.set_rules[rpl_set_rule.name]
                if set_rule.nh_address:
                    if not route_policy.address_family and set_rule.address_family.string == 'ipv4':
                        route_policy.address_family = 'ipv4'
                    elif not route_policy.address_family and set_rule.address_family.string == 'ipv6':
                        route_policy.address_family = 'ipv6'
                    elif route_policy.address_family.string == 'ipv4' and set_rule.address_family.string == 'ipv4':
                        continue
                    elif route_policy.address_family.string == 'ipv6' and set_rule.address_family.string == 'ipv6':
                        continue
                    else:
                        raise Exception(
                            f'Route-Policy {route_policy.profile} should not contain both ipv4 prefix-lists and ipv6 next-hop vice versa.')

    dc_rpl.dc_route_policy_type_copy = dc_rpl.dc_route_policy_type

    if dc_rpl.dc_route_policy_type.string == 'tenant' and hasattr(dc_rpl, 'tenant'):
        dc_rpl.tenant_copy = dc_rpl.tenant

    elif dc_rpl.dc_route_policy_type.string == 'vrf' and hasattr(dc_rpl, 'vrf'):
        dc_rpl.vrf_copy = dc_rpl.vrf

def _apply_template(dc_rpl):
    """Function to apply configurations to devices

    Args:
        dc_rpl: service node

    """
    template = ncs.template.Template(dc_rpl)
    template.apply('cisco-dc-services-fabric-routepolicy')
