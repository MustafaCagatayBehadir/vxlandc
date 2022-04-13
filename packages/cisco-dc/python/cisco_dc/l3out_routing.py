import ncs
from ipaddress import ip_address, IPv4Address
from multiprocessing import connection


def _configure_l3out_routing(root, bd, tctx, log):
    """Function to configure l3out routing

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    _set_hidden_leaves(root, bd, log)


def _set_hidden_leaves(root, bd, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        log: log object (self.log)

    """
    if bd.routing.exists():
        for bgp in bd.routing.bgp:
            if bgp.source_interface.interface == 'fabric-external-connection':
                vrf = root.cisco_dc__dc_site[bd.site].vrf_config[bd.vrf]
                l3out = bgp.source_interface.fabric_external_connection
                connections = root.cisco_dc__dc_site[bd.site].connections

                if (bd.tenant, bd.name, l3out.node) not in vrf.device:
                    vrf.device.create(bd.tenant, bd.name, l3out.node)

                if l3out.connection.string == 'uplink-to-dci-gw-01':
                    l3out.port_channel_id = connections.uplink_to_dci_gw_01
                else:
                    l3out.port_channel_id = connections.uplink_to_dci_gw_02

                if type(ip_address(bgp.peer_address)) is IPv4Address:
                    l3out.address = f'{str(IPv4Address(bgp.peer_address) + 1)}/30'
