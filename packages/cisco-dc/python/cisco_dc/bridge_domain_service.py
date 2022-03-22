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
    id_parameters = dict()
    _create_service_parameters(
        root, bd, tctx, id_parameters, log)
    _set_hidden_leaves(root, bd, id_parameters, log)
    _create_bd_config(root, bd, log)


def _create_service_parameters(root, bd, tctx, id_parameters, log):
    """Function to create vlan parameters and bd parameters

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        id_parameters: dict object
        log: log object (self.log)

    """
    resource_pools = root.cisco_dc__dc_site[bd.site].resource_pools
    id = [('network-vlan', resource_pools.l2_network_vlan),
          ('vrf-vlan', resource_pools.l3_vrf_vlan),
          ('l2vni', resource_pools.l2_vxlan_vni),
          ('l3vni', resource_pools.l3_vxlan_vni)]
    for parameter, pool_name in id:
        id_parameters[parameter] = id_allocator.id_read(
            tctx.username, root, pool_name, f'{bd.site}:{bd.tenant}:{bd.name}')
    log.info('Id Parameters :', id_parameters)


def _set_hidden_leaves(root, bd, id_parameters, log):
    """Function to create bd-service list at /dc-site/port-configs/bd-service

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        id_parameters: dict object
        log: log object (self.log)

    """
    port_groups = root.cisco_dc__dc_site[bd.site].port_configs
    attached_port_groups = bd.port_group
    for attached_port_group in attached_port_groups:
        port_group = port_groups[attached_port_group.name]
        ports = port_group.port_config
        if (bd.tenant, bd.name) not in port_group.bd_service:
            port_group.bd_service.create(bd.tenant, bd.name)
        for port in ports:
            if port.type == 'ethernet':
                eth = port.ethernet
                node = eth.node
                if (node, port.name) not in bd.port:
                    sa = bd.port.create(node, port.name)
                    sa.interface_id = eth.node_port
                    sa.mode = port.mode.string
                    sa.vlan = id_parameters['network-vlan']
                if node not in bd.device:
                    leaf = bd.device.create(node)
                    leaf.network_vlan, leaf.vrf_vlan, leaf.l2vni, leaf.l3vni = id_parameters.values()
            elif port.type == 'port-channel':
                pc = port.port_channel
                node = pc.node
                if (node, port.name) not in bd.direct_pc:
                    direct_pc = bd.direct_pc.create(node, port.name)
                    direct_pc.port_channel_id = pc.allocated_port_channel_id
                    direct_pc.mode = port.mode.string
                    direct_pc.vlan = id_parameters['network-vlan']
                if node not in bd.device:
                    leaf = bd.device.create(node)
                    leaf.network_vlan, leaf.vrf_vlan, leaf.l2vni, leaf.l3vni = id_parameters.values()
            elif port.type == 'vpc-port-channel':
                vpc = port.vpc_port_channel
                node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
                if (node_1, port.name) not in bd.virtual_pc:
                    virtual_pc = bd.virtual_pc.create(node_1, port.name)
                    virtual_pc.port_channel_id = vpc.allocated_port_channel_id
                    virtual_pc.mode = port.mode.string
                    virtual_pc.vlan = id_parameters['network-vlan']
                if (node_2, port.name) not in bd.virtual_pc:
                    virtual_pc = bd.virtual_pc.create(node_2, port.name)
                    virtual_pc.port_channel_id = vpc.allocated_port_channel_id
                    virtual_pc.mode = port.mode.string
                    virtual_pc.vlan = id_parameters['network-vlan']
                if node_1 not in bd.device:
                    leaf = bd.device.create(node_1)
                    leaf.network_vlan, leaf.vrf_vlan, leaf.l2vni, leaf.l3vni = id_parameters.values()
                if node_2 not in bd.device:
                    leaf = bd.device.create(node_2)
                    leaf.network_vlan, leaf.vrf_vlan, leaf.l2vni, leaf.l3vni = id_parameters.values()
            log.debug(
                f'Port {port.name} bridge-bomain {bd.name} hidden configuration is applied.')


def _create_bd_config(root, bd, log):
    """Function to create bridge-domain configuration

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        log: log object (self.log)

    """
    vars = ncs.template.Variables()
    utils.apply_template(bd, 'cisco-dc-services-fabric-bd-l2vni-service', vars)
    utils.apply_template(bd, 'cisco-dc-services-fabric-bd-vlan-service', vars)
