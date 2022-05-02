import ncs
from ncs.experimental import Query


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
    node_group = site.node_group[port.vpc_port_channel.node_group]
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


def is_node_vpc(root, port, port_parameters):
    """Function to check if node is Standalone or vPC

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        port_parameters: port configuration elements dictionary

    Returns:
        Boolean: True if node is a vPC node

    """
    site = root.cisco_dc__dc_site[port.site]
    if port_parameters['type'] == 'ethernet':
        return site.node[port_parameters['node']].node_type == 'vpc'
    elif port_parameters['type'] == 'port-channel':
        return site.node[port_parameters['node']].node_type == 'vpc'
    return True


def apply_template(service, template_name, template_vars):
    """Apply template by template name using service

    Args:
        service: service node
        template_name: name of template
        template_vars: template variables

    """
    template = ncs.template.Template(service)
    template.apply(template_name, template_vars)
