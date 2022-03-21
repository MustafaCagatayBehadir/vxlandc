from multiprocessing import pool
import ncs
from .resource_manager import id_allocator
from . import utils
from collections import defaultdict


class BridgeDomainServiceSelfComponent(ncs.application.NanoService):
    """
    NanoService callback handler for the self component of tenant service.
    """
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state,
                       proplist, component_proplist):
        '''Nano service create callback'''
        self.log.info('Nano create(state=', state, ')')

        # State functions
        if state == 'cisco-dc:id-allocated':
            _id_requested(root, service, tctx, self.log)

        elif state == 'cisco-dc:bridge-domain-configured':
            _configure_bridge_domain(root, service, tctx, self.log)


def _id_requested(root, bd, tctx, log):
    """Function to request vlan id & vni id from resource manager

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        tctx: transaction context (TransCtxRef)
        log: log object(self.log)
    """
    svc_xpath = "/cisco-dc:dc-site[fabric='{}']/tenant-service[name='{}']/bridge-domain[name='{}']"
    svc_xpath = svc_xpath.format(bd.site, bd.tenant, bd.name)
    resource_pools = root.cisco_dc__dc_site[bd.site].resource_pools
    id = [(bd.l2vni.vlan_id if bd.l2vni.vlan_id else -1, resource_pools.l2_network_vlan),
          (bd.l3vni.vlan_id if bd.l3vni.vlan_id else -1, resource_pools.l3_vrf_vlan),
          (bd.l2vni.vni_id if bd.l2vni.vni_id else -1, resource_pools.l2_vxlan_vni),
          (bd.l3vni.vni_id if bd.l3vni.vni_id else -1, resource_pools.l3_vxlan_vni)]
    for requested_id, pool_name in id:
        id_allocator.id_request(bd, svc_xpath, tctx.username, pool_name,
                                f'{bd.site}:{bd.tenant}:{bd.name}', False, requested_id)
        log.info(
            f'Id is requested from pool {pool_name} for service {bd.name}')


def _configure_bridge_domain(root, bd, tctx, log):
    """Function to configure bridge domain service

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    bd_parameters = defaultdict(dict)
    vlan_parameters = defaultdict(dict)
    _create_service_parameters(root, bd, tctx, bd_parameters, vlan_parameters, log)
    _create_bd_config(root, bd, bd_parameters, vlan_parameters, log)


def _create_service_parameters(root, bd, tctx, bd_parameters, vlan_parameters, log):
    """Function to create vlan parameters and bd parameters

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        bd_parameters: collections defaultdict object (defaultdict(dict))
        vlan_parameters: collections defaultdict object (defaultdict(dict))
        log: log object (self.log)

    """
    id_parameters = dict()
    resource_pools = root.cisco_dc__dc_site[bd.site].resource_pools
    id = [('network-vlan', resource_pools.l2_network_vlan),
          ('vrf-vlan', resource_pools.l3_vrf_vlan),
          ('l2vni', resource_pools.l2_vxlan_vni),
          ('l3vni', resource_pools.l3_vxlan_vni)]
    for parameter, pool_name in id:
        id_parameters[parameter] = id_allocator.id_read(
            tctx.username, root, pool_name, f'{bd.site}:{bd.tenant}:{bd.name}')
    log.info('Id Parameters :', id_parameters)
    port_groups = root.cisco_dc__dc_site[bd.site].port_configs
    attached_port_groups = bd.port_group
    for port_group in attached_port_groups:
        ports = port_groups[port_group.name].port_config
        for port in ports:
            vlan_dict = vlan_parameters[port.name]
            vlan_dict['mode'] = port.mode
            if port.port_type == 'ethernet':
                eth = port.ethernet
                node = eth.node
                vlan_dict['port-type'] = 'ethernet'
                vlan_dict['node'] = node
                vlan_dict['node-port'] = eth.node_port.as_list()
                vlan_dict['vlan-id'] = id_parameters['network-vlan']
                if not bd_parameters.get(node):
                    bd_parameters[node] = id_parameters
            elif port.port_type == 'port-channel':
                pc = port.port_channel
                node = pc.node
                vlan_dict['port-type'] = 'port-channel'
                vlan_dict['port-channel-id'] = pc.allocated_port_channel_id
                vlan_dict['node'] = node
                vlan_dict['node-port'] = pc.node_port.as_list()
                vlan_dict['vlan-id'] = id_parameters['network-vlan']
                if not bd_parameters.get(node):
                    bd_parameters[node] = id_parameters
            elif port.port_type == 'vpc-port-channel':
                vpc = port.vpc_port_channel
                node_group_id = vpc.node_group
                vlan_dict['port-type'] = 'vpc-port-channel'
                vlan_dict['port-channel-id'] = vpc.allocated_port_channel_id
                vlan_dict['node-group'] = node_group_id
                vlan_dict['node-1-port'] = vpc.node_1_port.as_list()
                vlan_dict['node-2-port'] = vpc.node_2_port.as_list()
                vlan_dict['vlan-id'] = id_parameters['network-vlan']
                node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
                if not bd_parameters.get(node_1):
                    bd_parameters[node_1] = id_parameters
                if not bd_parameters.get(node_2):
                    bd_parameters[node_2] = id_parameters
    log.debug(f'bridge-Domain: {bd.name}, bd-parameters:{bd_parameters}, vlan-parameters: {vlan_parameters}')


def _create_bd_config(root, bd, bd_parameters, vlan_parameters, log):
    """Function to create bridge-domain configuration

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        bd_parameters: collections defaultdict object (defaultdict(dict))
        vlan_parameters: collections defaultdict object (defaultdict(dict))
        log: log object (self.log)

    """
    vars = ncs.template.Variables()
    network_vlan_name, vrf_vlan_name, mcast_group = f'{bd.name}-network-vlan', f'{bd.name}-vrf-vlan', bd.mcast_group
    vars.add('NETWORK_VLAN_NAME', network_vlan_name)
    vars.add('VRF_VLAN_NAME', vrf_vlan_name)
    vars.add('MCAST_GROUP', mcast_group)
    for device, bd_dict in bd_parameters.items():
        vars.add('DEVICE', device)
        vars.add('NETWORK_VLAN_ID', bd_dict['network-vlan'])
        vars.add('VRF_VLAN_ID', bd_dict['vrf-vlan'])
        vars.add('L2VNI_ID', bd_dict['l2vni'])
        vars.add('L3VNI_ID', bd_dict['l3vni'])
        vars.add('VRF', bd.vrf)
        utils.apply_template(bd, 'cisco-dc-services-fabric-bd-l2vni-service', vars)
        log.debug(f'Device {device} bridge-bomain {bd.name} l2nvi configuration is applied.')
    for port_name, vlan_dict in vlan_parameters.items():
        vars.add('PORT_MODE', vlan_dict['mode'])
        vars.add('PORT_TYPE', vlan_dict['port-type'])
        vars.add('PO_ID', '')
        if vlan_dict['port-type'] == 'ethernet':
            vars.add('DEVICE', vlan_dict['node'])
            vars.add('VLAN_ID', vlan_dict['vlan-id'])
            for port in vlan_dict['node-port']:
                vars.add('ETH_ID', port)
                utils.apply_template(bd, 'cisco-dc-services-fabric-bd-vlan-service', vars)
        elif vlan_dict['port-type'] == 'port-channel':
            vars.add('DEVICE', vlan_dict['node'])
            vars.add('VLAN_ID', vlan_dict['vlan-id'])
            vars.add('ETH_ID', '')
            vars.add('PO_ID', vlan_dict['port-channel-id'])
            utils.apply_template(bd, 'cisco-dc-services-fabric-bd-vlan-service', vars)
        elif vlan_dict['port-type'] == 'vpc-port-channel':
            vars.add('PO_ID', vlan_dict['port-channel-id'])
            vars.add('ETH_ID', '')
            vars.add('PO_ID', vlan_dict['port-channel-id'])
            for device in utils.get_vpc_nodes_from_bd(root, bd, vlan_dict):
                vars.add('DEVICE', device)
                vars.add('VLAN_ID', vlan_dict['vlan-id'])
                utils.apply_template(bd, 'cisco-dc-services-fabric-bd-vlan-service', vars)
        log.debug(f'Port {port_name} bridge-bomain {bd.name} vlan configuration is applied.')
            


