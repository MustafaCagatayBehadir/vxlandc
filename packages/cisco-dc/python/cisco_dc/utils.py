import ncs
import _ncs
from ncs.experimental import Query
import json
from collections import defaultdict

from .nxapi import Nxapi
from .ttp_templates import vrf_config_template, route_table_template, route_table_longer_template

def get_port_channel_id_pool_name(root, port):
    """Function to return port-channel id pool name for a given node

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node

    Returns:
        String port-channel id pool if port type is port-channel or vpc-port-channel else None

    """
    if port.port_type == 'port-channel':
        site = root.cisco_dc__dc_site[port.site]
        device = port.port_channel.node
        po_id_pool = site.node[device].po_id_pool if site.node[device].node_type.string == 'standalone' else site.node_group[get_node_group(
            root, port, device)].po_id_pool
    elif port.port_type == 'vpc-port-channel':
        site = root.cisco_dc__dc_site[port.site]
        device_group = port.vpc_port_channel.node_group
        po_id_pool = site.node_group[device_group].po_id_pool
    return po_id_pool


def get_node_group(root, port, device):
    """Function to return vpc node group for a given vpc node

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        device: node name

    Returns:
        Integer node-group

    """
    trans = ncs.maagic.get_trans(root)
    query_path = f"/cisco-dc:dc-site[cisco-dc:fabric='{port.site}']/cisco-dc:node-group"
    with Query(trans, query_path, '/', ['id', 'node-1', 'node-2'], result_as=ncs.QUERY_STRING) as q:
        for r in q:
            if device in (r[1], r[2]):
                return int(r[0])


def get_description(port):
    """Function to create port description for Ethernet & Port-Channel & VPC Port-Channel on devices

    Args:
        port: service node

    Returns:
        String: Port description

    """
    if port.port_type == 'ethernet':
        return f'{port.name}:{port.mode}:{port.speed}'
    elif port.port_type == 'port-channel':
        return f'{port.name}:{port.mode}:{get_port_channel_speed(port)}'
    elif port.port_type == 'vpc-port-channel':
        return f'{port.name}:{port.mode}:{get_port_channel_speed(port)}'


def get_po_member_description(port):
    """Function to create port channel member port description

    Args:
        port: service node

    Returns:
        String: Port channel member port description

    """
    return f'{port.name}:MEMBER'


def get_port_channel_speed(port):
    """Function to get port channel speed

    Args:
        port: service node

    Returns:
        String: Port channel speed ex. 30G, 4G, 100G

    """
    if port.port_type == 'port-channel':
        return f'{len(port.port_channel.node_port) * int(port.speed.string[:-1])}G'
    elif port.port_type == 'vpc-port-channel':
        return f'{len(port.vpc_port_channel.node_1_port) * int(port.speed.string[:-1])}G'


def get_bum(speed):
    """Function to return BUM Values based on port speeds

    Args:
        speed: speed string value

    Returns:
        Float: BUM value

    """
    if speed == '1G':
        return 10.00
    elif speed == '10G':
        return 2.00
    return 0.50


def get_vpc_nodes_from_port(root, port):
    """Function to return vPC nodes

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node

    Returns:
        Tuple: vPC node1 & vPC node2 tuple object

    """
    site = root.cisco_dc__dc_site[port.site]
    if port.port_type == 'ethernet':
        eth = port.ethernet
        node = site.node[eth.node]
        node_group = site.node_group[node.vpc_id]
    elif port.port_type == 'port-channel':
        pc = port.port_channel
        node = site.node[pc.node]
        node_group = site.node_group[node.vpc_id]
    else:
        vpc = port.vpc_port_channel
        node_group = site.node_group[vpc.node_group]
    return node_group.node_1, node_group.node_2


def get_vpc_nodes_from_bd(root, bd, vlan_dict):
    """Function to return vPC nodes

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        vlan_dict: vlan configuration elements dictionary

    Returns:
        List: vPC node1 & vPC node2 list object

    """
    site = root.cisco_dc__dc_site[bd.site]
    node_group = site.node_group[vlan_dict.get('node-group')]
    return [node_group.node_1, node_group.node_2]


def get_vpc_nodes_from_l3out(root, bd, id):
    """Function to return vPC nodes

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        id: node group id

    Returns:
        List: vPC node1 & vPC node2 list object

    """
    site = root.cisco_dc__dc_site[bd.site]
    node_group = site.node_group[id]
    return [node_group.node_1, node_group.node_2]


def getIpAddress(addr):
    """Return the Ip part of a 'Ip/Net' string.

    Args:
        addr: IPv4 or IPv6 address with prefix length

    Returns:
        String: Ipv4 or IPv6 address

    """
    parts = addr.split('/')
    return parts[0]


def getIpPrefix(addr):
    """Return the Net part of a 'Ip/Net' string.

    Args:
        addr: IPv4 or IPv6 address with prefix length

    Returns:
        String: Prefix length    

    """
    parts = addr.split('/')
    return parts[1]


def get_kp_service_id(kp):
    kpath = str(kp)
    service = kpath[kpath.rfind("{") + 1:len(kpath) - 1]
    return service


def get_service_operation(op):
    if op == _ncs.dp.NCS_SERVICE_CREATE:
        return "SERVICE_CREATE"
    elif op == _ncs.dp.NCS_SERVICE_UPDATE:
        return "SERVICE_UPDATE"
    else:
        return "SERVICE_DELETE"


def get_network_vlan_name(bd):
    """Function to return network vlan name

    Args:
        bd: Service node

    Returns:
        String: Vlan name

    """
    vlan_name = f'{bd.tenant}:{bd.name}:network-vlan'
    return truncate_vlan_name(vlan_name) if len(vlan_name) > 32 else vlan_name


def get_vrf_vlan_name(vrf):
    """Function to return vrf vlan name

    Args:
        vrf: Service node

    Returns:
        String: Vlan name

    """
    vlan_name = f'{vrf.name}:vrf-vlan'
    return truncate_vlan_name(vlan_name) if len(vlan_name) > 32 else vlan_name


def get_static_route_name(bd):
    """Function to return static route name

    Args:
        bd: Service node

    Returns:
        String: Static route name

    """
    static_route_name = f'{bd.tenant}:{bd.name}'
    return truncate_static_route_name(static_route_name) if len(static_route_name) > 50 else static_route_name


def get_svi_description(bd):
    """Function to return svi description

    Args:
        bd: Service node

    Returns:
        String: svi description

    """
    return f'{bd.tenant}:{bd.name}:AGW'


def get_node_connections(site):
    """Function to return border-leaf connections

    Args:
        site: Maagic site object

    Returns:
        List: List of tuples

    """
    node_connections = list()
    nodes = [node.hostname for node in site.node if node.node_role == 'border-leaf']
    connections = ['uplink-to-dci-gw-01', 'uplink-to-dci-gw-02']
    for node in nodes:
        for connection in connections:
            node_connections.append((node, connection))
    return node_connections


def get_basic_authentication(root, auth_group):
    """Function to return basic authentication tuple

    Args:
        root: Maagic object pointing to the root of the CDB
        auth_group: Authentication group name

    Return:
        Tuple: username, password

    """
    default_map = root.ncs__devices.authgroups.group[auth_group].default_map
    username = default_map.remote_name
    password = default_map.remote_password
    password = _ncs.decrypt(password)
    return username, password


def get_route_policy_leaf_id_from_bd(bd, route_policy):
    """Function to return device list for the route-policy is used in bd

    Args:
        bd: Service node
        route_policy: Route policy ncs.maagic ListElement

    Return:
        List: List of device names

    """
    routing = bd.routing
    for bgp in routing.bgp:
        profiles = {
            peer_route_policy.profile for peer_route_policy in bgp.peer_route_policy}
        if route_policy.profile in profiles:
            nodes = bgp.source_interface.fabric_internal_connection.node
            return [node.leaf_id for node in nodes]
    return []


def get_route_policy_leaf_id_from_vrf(vrf, route_policy):
    """Function to return device list for the route-policy is used in vrf

    Args:
        vrf: Service node
        route_policy: Route policy ncs.maagic ListElement

    Return:
        List: List of device names

    """
    if vrf.direct.exists():
        direct = vrf.direct
        profiles = {direct.address_family_ipv4_policy,
                    direct.address_family_ipv6_policy}
        if route_policy.profile in profiles:
            nodes = vrf.device
            return [node.leaf_id for node in nodes]

    if vrf.static.exists():
        static = vrf.static
        profiles = {static.address_family_ipv4_policy,
                    static.address_family_ipv6_policy}
        if route_policy.profile in profiles:
            nodes = vrf.device
            return [node.leaf_id for node in nodes]

    routing = vrf.routing
    for bgp in routing.bgp:
        profiles = {
            peer_route_policy.profile for peer_route_policy in bgp.peer_route_policy}
        if route_policy.profile in profiles:
            return [bgp.source_interface.fabric_external_connection.node]
    return []


def get_cmd_dict_from_bd(root, bd, proplist, new_proplist):
    """Function to create command list to run on the reference DCI router

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        proplist: properties (list(tuple(str, str)), structure to pass data between callbacks
        new_proplist: new properties (list(tuple(str, str)) structure

    Return:
        Default Dict: Command default dict object

    """
    old_route_ref = json.loads(proplist[0][1]) if proplist else []
    new_route_ref = json.loads(new_proplist[0][1]) if new_proplist else []

    # Create diff route set
    diff_route_ref = [
        route for route in new_route_ref if route not in old_route_ref]

    internet_vrf = root.cisco_dc__dc_site[bd.site].fabric_parameters.internet_vrf

    cmd_list = defaultdict(list)

    if bd.vrf == internet_vrf:
        cmd_list = {prefix: [f'show route {prefix}',
                             f'show route longer-prefixes {prefix}'] for prefix in diff_route_ref}
    else:
        cmd_list = {prefix: [f'show route vrf {bd.vrf} {prefix}',
                             f'show route vrf {bd.vrf} longer-prefixes {prefix}'] for prefix in diff_route_ref}
        if cmd_list:
            cmd_list['vrf'] = ['show run vrf']
    return cmd_list


def get_vrf_from_dci_router(bd, r):
    """Function to get vrf from dci router otherwise raise exception

    Args:
        bd: service node
        r: scrapli response object

    Returns:
        String: Vrf name defined in dci router

    """
    data = r.ttp_parse_output(template=vrf_config_template)
    for results in data:
        for result in results['results']:
            if result.get('vrf').lower() == bd.vrf.lower():
                vrf = result.get('vrf')
                break
        else:
            raise Exception(f'Vrf {bd.vrf} can not be found on DCI.')
    return vrf


def truncate_vlan_name(vlan_name):
    """Function to truncate vlan name (vlan-name > 32 char is not allowed.)

    Args:
        vlan_name: Vlan name more than 32 char


    Return:
        String: Truncated vlan name

    """
    return f'{vlan_name[:29]}...'


def truncate_static_route_name(static_route_name):
    """Function to truncate static route name (static-route-name > 50 char is not allowed.)

    Args:
        static_route_name: Static route name more than 50 char


    Returns:
        String: Truncated static route name

    """
    return f'{static_route_name[:47]}...'


def update_command_dict(bd, vrf, cmd_dict):
    """Function to update command dictionary with dci vrf

    Args:
        bd: Service node
        vrf: DCI router vrf name
        cmd_dict: Default dict object

    Returns:
        Default dict: Command dictionary

    """
    cmd_dict.pop('vrf')
    for prefix, cmd_list in cmd_dict.items():
        cmd_dict[prefix] = [cmd.replace(bd.vrf, vrf) for cmd in cmd_list]
    return cmd_dict


def is_prefix_used(prefix, r, log):
    """Function to check if prefix is used in the current network and raise exception

    Args:
        prefix: prefix information ex. 10.1.1.0/24
        r: scrapli response object
        log: log object (self.log)

    """
    data = r.ttp_parse_output(template=route_table_template)
    log.info('Route Table Structured Results: ', data)
    for results in data:
        for result in results['results']:
            if int(result['mask']) > 22:
                raise Exception(f'Prefix {prefix} is already used in the network.')
    data = r.ttp_parse_output(template=route_table_longer_template)
    log.info('Route Table Longer Structured Results: ', data)
    for results in data:
        for result in results['results']:
            if int(result['mask']) > 22:
                raise Exception(f'Prefix {prefix} is already used in the network.')


def is_node_vpc(root, port):
    """Function to check if node is Standalone or vPC

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node

    Returns:
        Boolean: True if node is a vPC node

    """
    site = root.cisco_dc__dc_site[port.site]
    if port.port_type == 'ethernet':
        eth = port.ethernet
        node = eth.node
        return site.node[node].node_type == 'vpc'
    elif port.port_type == 'port-channel':
        pc = port.port_channel
        node = pc.node
        return site.node[node].node_type == 'vpc'
    return True


def send_show_command(device, cmd, log):
    """Function to send live status exec show command

    Args:
        device: Device ncs.maagic ListElement
        cmd: Command to run
        log: log object(self.log)

    Returns:
        result: Json Object
    """
    show = device.live_status.__getitem__('exec').show
    input = show.get_input()
    input.args = [cmd]
    result = show.request(input).result
    log.debug(f'Result :', result)
    return json.loads(result)


def nxapi_send_show_command(root, device, cmd, log):
    """Function to send show command via nxapi

    Args:
        root: Maagic object pointing to the root of the CDB
        device: Device ncs.maagic ListElement
        cmd: Command to run
        log: log object(self.log)

    Returns:
        result: Json Object
    """
    switch = device.address
    username, password = get_basic_authentication(root, device)
    nxapi = Nxapi(switch, username, password, log)
    return nxapi.send_show_command(cmd)


def apply_template(service, template_name, template_vars):
    """Apply template by template name using service

    Args:
        service: service node
        template_name: name of template
        template_vars: template variables

    """
    template = ncs.template.Template(service)
    template.apply(template_name, template_vars)
