import ncs
from ipaddress import ip_address, IPv4Address

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
    _raise_service_exceptions(root, dc_rpl, log)
    _set_hidden_leaves(root, dc_rpl, log)


def _raise_service_exceptions(root, dc_rpl, log):
    """Function to raise exception based on service prechecks

    Args:
        root: Maagic object pointing to the root of the CDB
        dc_rpl: service node
        log: log object(self.log)

    """
    for match_rule in dc_rpl.rules_set.match_rules:
        if match_rule.match_type == 'prefix-list':
            address_family = set()
            for prefix in match_rule.prefix:
                ip = utils.getIpAddress(prefix.ip)
                address_family.add('ipv4') if type(ip_address(
                    ip)) is IPv4Address else address_family.add('ipv6')
            if len(address_family) == 2:
                raise Exception(
                    f'Prefix-list {match_rule.name} should not contain both ipv4 and ipv6 addresses.')

    # In the iteration above we guaranteed that each prefix-list has only one address-family
    for route_policy in dc_rpl.route_policy:
        address_family = set()
        for match_and_set_group in route_policy.match_and_set_group:
            for rpl_match_rule in match_and_set_group.match_rules:
                match_rule = dc_rpl.rules_set.match_rules[rpl_match_rule.name]
                if match_rule.match_type == 'prefix-list':
                    for prefix in match_rule.prefix:
                        ip = utils.getIpAddress(prefix.ip)
                        address_family.add('ipv4') if type(ip_address(
                            ip)) is IPv4Address else address_family.add('ipv6')
                        break

        for match_and_set_group in route_policy.match_and_set_group:
            for rpl_set_rule in match_and_set_group.set_rules:
                set_rule = dc_rpl.rules_set.set_rules[rpl_set_rule.name]
                if set_rule.nh_address:
                    ip = set_rule.nh_address
                    address_family.add('ipv4') if type(ip_address(
                        ip)) is IPv4Address else address_family.add('ipv6')

        if len(address_family) == 2:
            raise Exception(
                f'Route-policy {route_policy.profile} should not contain both ipv4 and ipv6 address-families.')


def _set_hidden_leaves(root, dc_rpl, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        dc_rpl: service node
        log: log object (self.log)

    """
    for route_policy in dc_rpl.route_policy:
        
        for bd in route_policy.bd_device:
            for leaf_id in bd.leaf_id: 
                route_policy.device.create(bd.kp, leaf_id)
            log.info(
                f'Route policy {route_policy.profile} device is updated with bridge-domain keypath {bd.kp}.')

        for vrf in route_policy.vrf_device:
            for leaf_id in vrf.leaf_id: 
                route_policy.device.create(vrf.kp, leaf_id)
            log.info(
                f'Route policy {route_policy.profile} device is updated with bridge-domain keypath {vrf.kp}.')

    # In the _raise_service_exceptions function we guaranteed that each prefix-list has only one address-family
    for match_rule in dc_rpl.rules_set.match_rules:
        if match_rule.match_type == 'prefix-list':
            for prefix in match_rule.prefix:
                ip = utils.getIpAddress(prefix.ip)
                match_rule.address_family = 'ipv4' if type(
                    ip_address(ip)) is IPv4Address else 'ipv6'
                break

    for set_rule in dc_rpl.rules_set.set_rules:
        if set_rule.nh_address:
            ip = set_rule.nh_address
            set_rule.address_family = 'ipv4' if type(
                ip_address(ip)) is IPv4Address else 'ipv6'

    # In the _raise_service_exceptions function we guaranteed that each route-policy has only one address-family
    for route_policy in dc_rpl.route_policy:
        for match_and_set_group in route_policy.match_and_set_group:
            for rpl_match_rule in match_and_set_group.match_rules:
                match_rule = dc_rpl.rules_set.match_rules[rpl_match_rule.name]
                if match_rule.address_family == 'ipv4':
                    route_policy.address_family = 'ipv4'

                elif match_rule.address_family == 'ipv6':
                    route_policy.address_family = 'ipv6'

        # In the iteration above we try to set route-policy address-family if we can not continue with the next iteration
        if not route_policy.address_family:
            for match_and_set_group in route_policy.match_and_set_group:
                for rpl_set_rule in match_and_set_group.set_rules:
                    set_rule = dc_rpl.rules_set.set_rules[rpl_set_rule.name]
                    if set_rule.address_family == 'ipv4':
                        route_policy.address_family = 'ipv4'

                    elif set_rule.address_family == 'ipv6':
                        route_policy.address_family = 'ipv6'

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
