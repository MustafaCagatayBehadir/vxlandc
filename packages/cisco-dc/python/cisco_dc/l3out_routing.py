import ncs
from ipaddress import ip_address, IPv4Address, IPv6Address
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
    _apply_template(bd)


def _set_hidden_leaves(root, bd, address_family, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        address_family: set object
        log: log object (self.log)

    """
    if bd.routing.exists():
        for subnet in bd.bd_subnet:
            ip = utils.getIpAddress(subnet.address)
            if type(ip_address(ip)) is IPv4Address:
                address_family.add('ipv4')
            elif type(ip_address(ip)) is IPv6Address:
                address_family.add('ipv6')

        for bgp in bd.routing.bgp:
            ip = bgp.peer_address
            if type(ip_address(ip)) is IPv4Address and 'ipv4' in address_family:
                bgp.address_family = 'ipv4'
            elif type(ip_address(ip)) is IPv6Address and 'ipv6' in address_family:
                bgp.address_family = 'ipv6'
            else:
                raise Exception(
                    f'BGP neighbor address and bridge-domain subnet address-family should match.')

            if bgp.source_interface.interface == 'fabric-external-connection':
                vrf = root.cisco_dc__dc_site[bd.site].vrf_config[bd.vrf]
                l3out = bgp.source_interface.fabric_external_connection
                connections = root.cisco_dc__dc_site[bd.site].connections

                if (bd._path, l3out.node) not in vrf.device:
                    vrf.device.create(bd._path, l3out.node)

                if l3out.connection.string == 'uplink-to-dci-gw-01':
                    l3out.port_channel_id = connections.uplink_to_dci_gw_01
                else:
                    l3out.port_channel_id = connections.uplink_to_dci_gw_02

                if type(ip_address(bgp.peer_address)) is IPv4Address:
                    l3out.address = f'{str(IPv4Address(bgp.peer_address) + 1)}/30'
                elif type(ip_address(bgp.peer_address)) is IPv6Address:
                    l3out.address = f'{str(IPv6Address(bgp.peer_address) + 1)}/64'


def _apply_template(bd):
    """Function to apply configurations to devices

    Args:
        bd: service node

    """
    template = ncs.template.Template(bd)
    vars = ncs.template.Variables()
    template.apply('cisco-dc-services-fabric-l3out-routing-bgp')