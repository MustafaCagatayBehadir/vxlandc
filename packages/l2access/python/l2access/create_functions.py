import l2access.helpers as helpers
from .resource_manager import id_allocator
import ncs


def create_l2access_parameters(root, tctx, l2access, vlan_trunking_parameters, l2vni_parameters, log):
    """Function to create vlan trunking parameters and l2vni parameters

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node
        vlan_trunking_parameters: empty collections defaultdict object (defaultdict(dict))
        l2vni_parameters: empty collections defaultdict object (defaultdict(dict))
        log: log object (self.log)

    """
    create_l2access_parameters_tenant_epg(
        root, tctx, l2access, vlan_trunking_parameters, l2vni_parameters)
    create_l2access_parameters_external_tenant_epg(
        root, tctx, l2access, vlan_trunking_parameters, l2vni_parameters)
    log.info('L2 Access EPG Parameters: ', vlan_trunking_parameters)
    log.info('L2VNI Parameters: ', l2vni_parameters)


def create_l2access_parameters_tenant_epg(root, tctx, l2access, vlan_trunking_parameters, l2vni_parameters):
    """Function to create vlan trunking parameters and l2vni parameters for internal tenant epg

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node
        vlan_trunking_parameters: collections defaultdict object (defaultdict(dict))
        l2vni_parameters: collections defaultdict object (defaultdict(dict))

    """
    tenant = root.vxlandc_core__vxlandc.vxlandc_core__sites.vxlandc_core__site[
        l2access.site].vxlandc_core__tenants.vxlandc_core__tenant[l2access.tenant]
    tenant_epg = l2access.endpoint_groups.tenant_endpoint_group
    port_groups = tenant.l1access__port_groups
    ports = tenant.l1access__ports
    vni_id = id_allocator.id_read(
        tctx.username, root, helpers.get_vni_id_pool_name(root, l2access), l2access.name)
    vlan_id = id_allocator.id_read(
        tctx.username, root, helpers.get_vlan_id_pool_name(root, l2access), l2access.name)
    for epg in tenant_epg:
        for port_name in port_groups.port_group[epg.name].port:
            vlan_trunking_dict = vlan_trunking_parameters[ports.port[port_name].name]
            vlan_trunking_dict['mode'] = ports.port[port_name].mode.string
            if ports.port[port_name].port_type == 'ethernet':
                vlan_id = id_allocator.id_read(tctx.username, root, helpers.get_vlan_id_pool_name(
                    root, l2access, ports.port[port_name]), l2access.name)
                eth = ports.port[port_name].ethernet
                node = eth.node
                vlan_trunking_dict['port-type'] = 'ethernet'
                vlan_trunking_dict['node'] = node
                vlan_trunking_dict['node-port'] = eth.node_port.as_list()
                vlan_trunking_dict['vlan-id'] = vlan_id
                if not l2vni_parameters.get(node):
                    l2vni_parameters[node] = {
                        'vlan-id': vlan_id, 'vni-id': vni_id}
            elif ports.port[port_name].port_type == 'port-channel':
                pc = ports.port[port_name].port_channel
                node = pc.node
                vlan_trunking_dict['port-type'] = 'port-channel'
                vlan_trunking_dict['port-channel-id'] = pc.allocated_port_channel_id
                vlan_trunking_dict['node'] = node
                vlan_trunking_dict['node-port'] = pc.node_port.as_list()
                vlan_trunking_dict['vlan-id'] = vlan_id
                if not l2vni_parameters.get(node):
                    l2vni_parameters[node] = {
                        'vlan-id': vlan_id, 'vni-id': vni_id}
            elif ports.port[port_name].port_type == 'vpc-port-channel':
                vpc = ports.port[port_name].vpc_port_channel
                node_group_id = vpc.node_group
                vlan_trunking_dict['port-type'] = 'vpc-port-channel'
                vlan_trunking_dict['port-channel-id'] = vpc.allocated_port_channel_id
                vlan_trunking_dict['node-group'] = node_group_id
                vlan_trunking_dict['node-1-port'] = vpc.node_1_port.as_list()
                vlan_trunking_dict['node-2-port'] = vpc.node_2_port.as_list()
                vlan_trunking_dict['vlan-id'] = vlan_id
                node_1, node_2 = helpers.get_vpc_nodes(
                    root, l2access.site, node_group_id)
                if not l2vni_parameters.get(node_1):
                    l2vni_parameters[node_1] = {
                        'vlan-id': vlan_id, 'vni-id': vni_id}
                if not l2vni_parameters.get(node_2):
                    l2vni_parameters[node_1] = {
                        'vlan-id': vlan_id, 'vni-id': vni_id}


def create_l2access_parameters_external_tenant_epg(root, tctx, l2access, vlan_trunking_parameters, l2vni_parameters):
    """Function to create vlan trunking parameters and l2vni parameters for external tenant epg

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node
        vlan_trunking_parameters: collections defaultdict object (defaultdict(dict))
        l2vni_parameters: collections defaultdict object (defaultdict(dict))

    """
    external_tenant_epg = l2access.endpoint_groups.external_tenant_endpoint_group
    vni_id = id_allocator.id_read(
        tctx.username, root, helpers.get_vni_id_pool_name(root, l2access), l2access.name)
    for epg in external_tenant_epg:
        tenant = root.vxlandc_core__vxlandc.vxlandc_core__sites.vxlandc_core__site[
            l2access.site].vxlandc_core__tenants.vxlandc_core__tenant[epg.tenant]
        port_groups = tenant.l1access__port_groups
        ports = tenant.l1access__ports
        for port_name in port_groups.port_group[epg.name].port:
            vlan_trunking_dict = vlan_trunking_parameters[ports.port[port_name].name]
            vlan_trunking_dict['mode'] = ports.port[port_name].mode.string
            if ports.port[port_name].port_type == 'ethernet':
                vlan_id = id_allocator.id_read(tctx.username, root, helpers.get_vlan_id_pool_name(
                    root, l2access, ports.port[port_name]), l2access.name)
                eth = ports.port[port_name].ethernet
                node = eth.node
                vlan_trunking_dict['port-type'] = 'ethernet'
                vlan_trunking_dict['node'] = node
                vlan_trunking_dict['node-port'] = eth.node_port.as_list()
                vlan_trunking_dict['vlan-id'] = vlan_id
                if not l2vni_parameters.get(node):
                    l2vni_parameters[node] = {
                        'vlan-id': vlan_id, 'vni-id': vni_id}
            elif ports.port[port_name].port_type == 'port-channel':
                pc = ports.port[port_name].port_channel
                node = pc.node
                vlan_trunking_dict['port-type'] = 'port-channel'
                vlan_trunking_dict['port-channel-id'] = pc.allocated_port_channel_id
                vlan_trunking_dict['node'] = node
                vlan_trunking_dict['node-port'] = pc.node_port.as_list()
                vlan_trunking_dict['vlan-id'] = vlan_id
                if not l2vni_parameters.get(node):
                    l2vni_parameters[node] = {
                        'vlan-id': vlan_id, 'vni-id': vni_id}
            elif ports.port[port_name].port_type == 'vpc-port-channel':
                vpc = ports.port[port_name].vpc_port_channel
                node_group_id = vpc.node_group
                vlan_trunking_dict['port-type'] = 'vpc-port-channel'
                vlan_trunking_dict['port-channel-id'] = vpc.allocated_port_channel_id
                vlan_trunking_dict['node-group'] = node_group_id
                vlan_trunking_dict['node-1-port'] = vpc.node_1_port.as_list()
                vlan_trunking_dict['node-2-port'] = vpc.node_2_port.as_list()
                vlan_trunking_dict['vlan-id'] = vlan_id
                node_1, node_2 = helpers.get_vpc_nodes(
                    root, l2access.site, node_group_id)
                if not l2vni_parameters.get(node_1):
                    l2vni_parameters[node_1] = {
                        'vlan-id': vlan_id, 'vni-id': vni_id}
                if not l2vni_parameters.get(node_2):
                    l2vni_parameters[node_1] = {
                        'vlan-id': vlan_id, 'vni-id': vni_id}


def allocate_vlan_id(root, l2access, tctx, log):
    """Function to allocate vlan id from resource manager

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    requested_id = l2access.vlan_id if l2access.vlan_id else -1
    svc_xpath = "/vxlandc-core:vxlandc/sites/site[fabric='{}']/tenants/tenant[name='{}']/l2access:l2-fabric-services/l2-fabric-service[name='{}']"
    svc_xpath = svc_xpath.format(l2access.site, l2access.tenant, l2access.name)
    id_allocator.id_request(l2access, svc_xpath, tctx.username, helpers.get_vlan_id_pool_name(
        root, l2access), l2access.name, False, requested_id)
    log.info(f'Vlan id is requested for service {l2access.name}')


def allocate_vni_id(root, l2access, tctx, log):
    """Function to allocate vni id from resource manager

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    requested_id = l2access.vni_id if l2access.vlan_id else -1
    svc_xpath = "/vxlandc-core:vxlandc/sites/site[fabric='{}']/tenants/tenant[name='{}']/l2access:l2-fabric-services/l2-fabric-service[name='{}']"
    svc_xpath = svc_xpath.format(l2access.site, l2access.tenant, l2access.name)
    id_allocator.id_request(l2access, svc_xpath, tctx.username, helpers.get_vni_id_pool_name(
        root, l2access), l2access.name, False, requested_id)
    log.info(f'Vni id is requested for service {l2access.name}')


def create_vlan(l2access, l2vni_parameters):
    """Function to create l2vni configuration

    Args:
        l2access: service node
        l2vni_parameters: collections defaultdict object (defaultdict(dict))
        log: log object (self.log)

    """
    tvars = ncs.template.Variables()
    vlan_name, mcast_group = l2access.name, l2access.mcast_group
    tvars.add('VLAN_NAME', vlan_name)
    tvars.add('MCAST_GROUP', mcast_group)
    for device in l2vni_parameters:
        tvars.add('DEVICE', device)
        tvars.add('VLAN_ID', l2vni_parameters[device]['vlan-id'])
        tvars.add('VNI_ID', l2vni_parameters[device]['vni-id'])
        helpers.apply_template(l2access, 'l2vni', tvars)


def create_vlan_trunking(root, l2access, vlan_trunking_parameters):
    """Function to allow vlan under access or trunk ports

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node
        vlan_trunking_parameters: collections defaultdict object (defaultdict(dict))       

    """
    tvars = ncs.template.Variables()
    for vlan_trunking_dict in vlan_trunking_parameters.values():
        tvars.add('PORT_MODE', vlan_trunking_dict['mode'])
        tvars.add('PORT_TYPE', vlan_trunking_dict['port-type'])
        if vlan_trunking_dict['port-type'] == 'ethernet':
            tvars.add('DEVICE', vlan_trunking_dict['node'])
            tvars.add('VLAN_ID', vlan_trunking_dict['vlan-id'])
            tvars.add('PO_ID', '')
            for port in vlan_trunking_dict['node-port']:
                tvars.add('ETH_ID', port)
                helpers.apply_template(l2access, 'vlan-trunking', tvars)
        elif vlan_trunking_dict['port-type'] == 'port-channel':
            tvars.add('DEVICE', vlan_trunking_dict['node'])
            tvars.add('VLAN_ID', vlan_trunking_dict['vlan-id'])
            tvars.add('PO_ID', vlan_trunking_dict['port-channel-id'])
            tvars.add('ETH_ID', '')
            helpers.apply_template(l2access, 'vlan-trunking', tvars)
        elif vlan_trunking_dict['port-type'] == 'vpc-port-channel':
            tvars.add('PO_ID', vlan_trunking_dict['port-channel-id'])
            tvars.add('ETH_ID', '')
            for device in helpers.get_vpc_nodes(root, l2access.site, vlan_trunking_dict['node-group']):
                tvars.add('DEVICE', device)
                tvars.add('VLAN_ID', vlan_trunking_dict['vlan-id'])
                helpers.apply_template(l2access, 'vlan-trunking', tvars)
