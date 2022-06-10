import ncs
from ipaddress import ip_address, IPv4Address, IPv6Address


def _configure_l3out_routing(root, vrf, tctx, log):
    """Function to configure l3out routing

    Args:
        root: Maagic object pointing to the root of the CDB
        vrf: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    _set_hidden_leaves(root, vrf, log)


def _set_hidden_leaves(root, vrf, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        vrf: service node
        log: log object (self.log)

    """
    if vrf.routing:

        routing = vrf.routing

        for bgp in routing.bgp:

            bgp.as_number = root.cisco_dc__dc_site[vrf.site].fabric_parameters.as_number

            l3out = bgp.source_interface.fabric_external_connection
            connections = root.cisco_dc__dc_site[vrf.site].connections

            if l3out.connection.string == 'uplink-to-dci-gw-01':
                l3out.port_channel_id = connections.uplink_to_dci_gw_01
            else:
                l3out.port_channel_id = connections.uplink_to_dci_gw_02

            if type(ip_address(bgp.peer_address)) is IPv4Address:
                l3out.address = f'{str(IPv4Address(bgp.peer_address) + 1)}/30'
                bgp.address_family = 'ipv4'
            elif type(ip_address(bgp.peer_address)) is IPv6Address:
                l3out.address = f'{str(IPv6Address(bgp.peer_address) + 1)}/64'
                bgp.address_family = 'ipv6'

            l3out.vlan = vrf.fabric_external_vlan_id

            profiles = {
                peer_route_policy.profile for peer_route_policy in bgp.peer_route_policy}
            if profiles:
                dc_route_policies = root.cisco_dc__dc_site[vrf.site].dc_route_policy
                for dc_route_policy in dc_route_policies:
                    if hasattr(dc_route_policy, 'vrf') and dc_route_policy.vrf == vrf.name:
                        for route_policy in dc_route_policy.route_policy:
                            if route_policy.profile in profiles:
                                route_policy.attached_vrf_kp.create(
                                    vrf._path)
                                log.info(
                                    f'Dc route policy {dc_route_policy.name} route policy {route_policy.profile} attached vrf keypath leaf-list is updated by vrf {vrf.name}.')


def _apply_template(vrf):
    """Function to apply configurations to devices

    Args:
        vrf: service node

    """
    template = ncs.template.Template(vrf)
    vars = ncs.template.Variables()
    vars.add('VRF', vrf.name)
    template.apply('cisco-dc-services-fabric-vrf-l3out-routing-bgp', vars)
