import ncs
from ncs.experimental import Query


def get_node_group(root, l2access, device):
    """Function to return vpc node group for a given vpc node

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node
        device: node name

    Returns:
        Integer node-group
    """
    trans = ncs.maagic.get_trans(root)
    query_path = f"/vxlandc-core:vxlandc/vxlandc-core:sites/vxlandc-core:site[vxlandc-core:fabric='{l2access.site}']/vxlandc-core:node-group"
    with Query(trans, query_path, '/', ['id', 'node-1', 'node-2'], result_as=ncs.QUERY_STRING) as q:
        for r in q:
            if device in (r[1], r[2]):
                return int(r[0])


def get_vlan_id_pool_name(root, l2access):
    """Function to return vlan id pool name for a given site

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: l2access service node

    Returns:
        String vlan id pool name

    """
    site = root.vxlandc_core__vxlandc.vxlandc_core__sites.vxlandc_core__site[l2access.site]
    return site.resource_pools.l2_network_vlan


def get_vni_id_pool_name(root, l2access):
    """Function to return vni id pool name for a given site

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node

    Returns:
        String vni pool
    """
    site = root.vxlandc_core__vxlandc.vxlandc_core__sites.vxlandc_core__site[l2access.site]
    return site.resource_pools.l2_vxlan_vni


def get_vpc_nodes(root, site_name, node_group_id):
    """Function to return vPC nodes

    Args:
        site: site name
        node_group: node-group id

    Returns:
        Tuple: vPC node1 & vPC node2 tuple object 
    """
    node_group = root.vxlandc_core__vxlandc.sites.site[site_name].node_group[node_group_id]
    return node_group.node_1, node_group.node_2


def apply_template(service, template_name, template_vars):
    """Apply template by template name using service

    Args:
        service: service node
        template_name: name of template
        template_vars: template variables
    """
    template = ncs.template.Template(service)
    template.apply(template_name, template_vars)
