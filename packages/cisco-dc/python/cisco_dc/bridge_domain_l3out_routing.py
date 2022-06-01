import ncs
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address, IPv4Network, IPv6Network
from . import utils


def _configure_l3out_routing(root, bd, tctx, log):
    """Function to configure l3out routing

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    address_family = set()
    _set_hidden_leaves(root, bd, address_family, log)


def _set_hidden_leaves(root, bd, address_family, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        address_family: set object
        log: log object (self.log)

    """
    if bd.routing:

        routing = bd.routing

        for subnet in bd.bd_subnet:
            ip = utils.getIpAddress(subnet.address)
            if type(ip_address(ip)) is IPv4Address:
                address_family.add('ipv4')
            elif type(ip_address(ip)) is IPv6Address:
                address_family.add('ipv6')

        for bgp in routing.bgp:
            ip = bgp.peer_address
            if type(ip_address(ip)) is IPv4Address and 'ipv4' in address_family:
                bgp.address_family = 'ipv4'
            elif type(ip_address(ip)) is IPv6Address and 'ipv6' in address_family:
                bgp.address_family = 'ipv6'
            else:
                raise Exception(
                    f'BGP neighbor address and bridge-domain subnet address-family should match.')

            bgp.as_number = root.cisco_dc__dc_site[bd.site].fabric_parameters.as_number

            devices = [
                node.leaf_id for node in bgp.source_interface.fabric_internal_connection.node]
            if hasattr(bgp.source_interface, 'fabric_internal_connection'):
                profiles = {
                    peer_route_policy.profile for peer_route_policy in bgp.peer_route_policy}
                if profiles:
                    dc_route_policies = root.cisco_dc__dc_site[bd.site].dc_route_policy
                    for dc_route_policy in dc_route_policies:
                        if hasattr(dc_route_policy, 'tenant') and dc_route_policy.tenant == bd.tenant:
                            for route_policy in dc_route_policy.route_policy:
                                if route_policy.profile in profiles:
                                    for device in devices:
                                        if (bd._path, device) not in route_policy.device:
                                            route_policy.device.create(
                                                bd._path, device)
                                    log.info(
                                        f'Route-Policy {route_policy.profile} is activated by tenant {bd.tenant} bridge-domain {bd.name} routing bgp {bgp.peer_address}')

        if routing.static_route.exists():
            static_route = routing.static_route

            for destination in static_route.destination:
                ip = destination.address
                if type(ip_network(ip)) is IPv4Network and 'ipv4' in address_family:
                    destination.address_family = 'ipv4'
                elif type(ip_network(ip)) is IPv6Network and 'ipv6' in address_family:
                    destination.address_family = 'ipv6'
                else:
                    raise Exception(
                        f'Static route destination address and bridge-domain subnet address-family should match.')

                source_node = destination.source_node

                if source_node.template == 'apply-specific-nodes':
                    l3out = source_node.apply_specific_nodes

                    for node in l3out.node:

                        for device in bd.device:
                            if device.leaf_id == node.leaf_id:
                                break
                        else:
                            raise Exception(
                                f'Node {node.leaf_id} is not attached to bd {bd.name}')

                        if (l3out._path, node.leaf_id) not in source_node.device:
                            device = source_node.device.create(
                                l3out._path, node.leaf_id)
                            device.ip_nexthop = destination.ip_nexthop
                            device.address_family = destination.address_family
                            log.info(
                                f'Device {device.leaf_id} is created by routing static destination {destination.address} fabric-internal-connection apply-specific-template')

                    for node_group in l3out.node_group:

                        for leaf_id in utils.get_vpc_nodes_from_l3out(root, bd, node_group.id):

                            for device in bd.device:
                                if device.leaf_id == leaf_id:
                                    break
                            else:
                                raise Exception(
                                    f'Node {leaf_id} is not attached to bd {bd.name}')

                            if (l3out._path, leaf_id) not in source_node.device:
                                device = source_node.device.create(
                                    l3out._path, leaf_id)
                                device.ip_nexthop = destination.ip_nexthop
                                device.address_family = destination.address_family
                                log.info(
                                    f'Device {device.leaf_id} is created by routing static destination {destination.address} fabric-internal-connection apply-specific-template')

                elif source_node.template == 'apply-all-nodes':
                    l3out = source_node.apply_all_nodes

                    for device in bd.device:

                        if (l3out._path, device.leaf_id) not in source_node.device:
                            device = source_node.device.create(
                                l3out._path, device.leaf_id)
                            device.ip_nexthop = destination.ip_nexthop
                            device.address_family = destination.address_family
                            log.info(
                                f'Device {device.leaf_id} is created by routing static destination {destination.address} fabric-internal-connection apply-default-template')


def _apply_template(bd):
    """Function to apply configurations to devices

    Args:
        bd: service node

    """
    template = ncs.template.Template(bd)
    vars = ncs.template.Variables()
    vars.add('VRF', bd.vrf)
    vars.add('STATIC_ROUTE_NAME', utils.get_static_route_name(bd))
    template.apply('cisco-dc-services-fabric-bd-l3out-routing-bgp', vars)
    template.apply('cisco-dc-services-fabric-l3out-routing-static', vars)
