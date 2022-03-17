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


def get_description(port, port_parameters):
    """Function to create port description for Ethernet & Port-Channel & VPC Port-Channel on devices

    Args:
        port: service node
        port_parameters: port configuration elements dictionary

    Returns:
        String: Port description

    """
    tenant = port._parent._parent._parent.name
    description = f"{tenant}_{port_parameters['name']}_{port_parameters['mode']}_{port_parameters['speed']}".upper(
    )
    if port_parameters['type'] == 'ethernet':
        return f"{description}_ETH"
    elif port_parameters['type'] == 'port-channel':
        return f"{description}_PC"
    return f"{description}_VPC"


def get_po_member_description(node_port, port_parameters):
    """Function to create port channel member port description

    Args:
        node_port: Port id like 1/10
        port_parameters: port configuration elements dictionary

    Returns:
        String: Port channel member port description

    """
    return f"PO{port_parameters['port-channel-id']}_MEMBER_ETH_{node_port}"


def get_bum(port_parameters):
    """Function to return BUM Values based on port speeds

    Args:
        port_parameters: port configuration elements dictionary

    Returns:
        Float: BUM value

    """
    if port_parameters['speed'] == '1G':
        return 10.00
    elif port_parameters['speed'] == '10G':
        return 2.00
    return 0.50


def get_vpc_nodes(root, port):
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
    query_path = f"/vxlandc-core:vxlandc/vxlandc-core:sites/vxlandc-core:site[vxlandc-core:fabric='{port.site}']/vxlandc-core:node-group"
    with Query(trans, query_path, '/', ['id', 'node-1', 'node-2'], result_as=ncs.QUERY_STRING) as q:
        for r in q:
            if device in (r[1], r[2]):
                return int(r[0])


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
