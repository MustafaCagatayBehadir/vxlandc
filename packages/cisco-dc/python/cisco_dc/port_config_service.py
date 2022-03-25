import ncs
import _ncs
import ncs.maapi as maapi
import ncs.maagic as maagic
from . import utils
from .resource_manager import id_allocator
from collections import defaultdict


class PortServiceSelfComponent(ncs.application.NanoService):
    """
    NanoService callback handler for the self component of port-config service.
    """
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state,
                       proplist, component_proplist):
        '''Nano service create callback'''
        self.log.info('Nano create(state=', state, ')')

        # State functions
        if state == 'cisco-dc:id-allocated':
            _id_requested(root, service, tctx, self.log)

        elif state == 'cisco-dc:port-configured':
            _configure_port(root, service, tctx, self.log)


def _id_requested(root, port, tctx, log):
    """Function to request port-channel id from resource manager

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        tctx: transaction context (TransCtxRef)
        log: log object(self.log)

    """
    if port.port_type == 'port-channel':
        requested_id = port.port_channel.port_channel_id if port.port_channel.port_channel_id else -1
        svc_xpath = "/cisco-dc:dc-site[cisco-dc:fabric='{}']/cisco-dc:port-configs[cisco-dc:name='{}']/cisco-dc:port-config[cisco-dc:name='{}']"
        svc_xpath = svc_xpath.format(port.site, port.port_group, port.name)
        id_allocator.id_request(port, svc_xpath, tctx.username, utils.get_port_channel_id_pool_name(
            root, port), f'{port.site}:{port.port_group}:{port.name}', False, requested_id)
        log.info(f'Port-Channel id is requested for port {port.name}')
    elif port.port_type == 'vpc-port-channel':
        requested_id = port.vpc_port_channel.port_channel_id if port.vpc_port_channel.port_channel_id else -1
        svc_xpath = "/cisco-dc:dc-site[cisco-dc:fabric='{}']/cisco-dc:port-configs[cisco-dc:name='{}']/cisco-dc:port-config[cisco-dc:name='{}']"
        svc_xpath = svc_xpath.format(port.site, port.port_group, port.name)
        id_allocator.id_request(port, svc_xpath, tctx.username, utils.get_port_channel_id_pool_name(
            root, port), f'{port.site}:{port.port_group}:{port.name}', False, requested_id)
        log.info(f'Port-Channel id is requested for port {port.name}')


def _configure_port(root, port, tctx, log):
    """Function to configure port service

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    id_parameters = dict()
    _create_service_parameters(
        root, port, tctx, id_parameters, log)
    _set_hidden_leaves(root, port, tctx, id_parameters, log)
    _create_port_config(port)


def _create_service_parameters(root, port, tctx, id_parameters, log):
    """Function to create port parameters for Ethernet & Port-Channel & VPC Port-Channel

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        tctx: transaction context (TransCtxRef)
        id_parameters: dict object
        log: log object(self.log)

    """
    if port.port_type == 'port-channel':
        id_parameters['port-channel-id'] = id_allocator.id_read(
            tctx.username, root, utils.get_port_channel_id_pool_name(root, port), f'{port.site}:{port.port_group}:{port.name}')
    elif port.port_type == 'vpc-port-channel':
        id_parameters['port-channel-id'] = id_allocator.id_read(
            tctx.username, root, utils.get_port_channel_id_pool_name(root, port), f'{port.site}:{port.port_group}:{port.name}')


def _set_hidden_leaves(root, port, tctx, id_parameters, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        tctx: transaction context (TransCtxRef)
        id_parameters: dict object
        log: log object(self.log)    

    """
    if port.port_type == 'ethernet':
        port.type = 'ethernet'
    elif port.port_type == 'port-channel':
        port.type = 'port-channel'
        port.port_channel.allocated_port_channel_id = id_parameters.get(
            'port-channel-id')
    elif port.port_type == 'vpc-port-channel':
        port.type = 'vpc-port-channel'
        port.vpc_port_channel.allocated_port_channel_id = id_parameters.get(
            'port-channel-id')
        node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
        vpc_nodes = [(node_1, port.vpc_port_channel.node_1_port),
                     (node_2, port.vpc_port_channel.node_2_port)]
        for node, node_port in vpc_nodes:
            vpc_node = port.vpc_port_channel.node.create(node)
            vpc_node.node_port = node_port
    port.bum = utils.get_bum(port.speed)
    bd_services = root.cisco_dc__dc_site[port.site].port_configs[port.port_group].bd_service
    for bd_service in bd_services:
        bd = ncs.maagic.cd(root, bd_service.kp)
        if port.port_type == 'ethernet':
            eth = port.ethernet
            if (eth.node, port.name) not in bd.port:
                bd_port = bd.port.create(eth.node, port.name)
                bd_port.interface_id = eth.node_port
            else:
                bd.port[eth.node, port.name].interface_id = eth.node_port
        elif port.port_type == 'port-channel':
            pc = port.port_channel
            if (pc.node, port.name) not in bd.direct_pc:
                bd_direct_pc = bd.direct_pc.create(pc.node, port.name)
                bd_direct_pc.port_channel_id = pc.allocated_port_channel_id
            else:
                bd.direct_pc[pc.node,
                             port.name].port_channel_id = pc.allocated_port_channel_id
        elif port.port_type == 'vpc-port-channel':
            vpc = port.vpc_port_channel
            node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
            if (node_1, port.name) not in bd.virtual_pc:
                bd_virtual_pc = bd.virtual_pc.create(node_1, port.name)
                bd_virtual_pc.port_channel_id = vpc.allocated_port_channel_id
            else:
                bd_virtual_pc[node_1,
                              port.name].port_channel_id = vpc.allocated_port_channel_id
            if (node_2, port.name) not in bd.virtual_pc:
                bd_virtual_pc = bd.virtual_pc.create(node_2, port.name)
                bd_virtual_pc.port_channel_id = vpc.allocated_port_channel_id
            else:
                bd_virtual_pc[node_2,
                              port.name].port_channel_id = vpc.allocated_port_channel_id
        log.info(f'Bridge-domain {bd.name} is activated by port {port.name}')


def _create_port_config(port):
    """Function to create port configuration

    Args:
        port: service node

    """
    template = ncs.template.Template(port)
    template.apply('cisco-dc-services-fabric-port-service')


class PortConfigServiceValidator(object):
    def __init__(self, log):
        self.log = log

    def cb_validate(self, tctx, kp, newval):
        '''
        Validating node port values are not overlapping for port-configs services
        '''

        try:
            self.log.debug("Validating port-config service")
            m = maapi.Maapi()
            th = m.attach(tctx)

            service = maagic.get_node(th, str(kp))
            dc_site = maagic.cd(service, '../..')
            fabric = dc_site.fabric

            # raise Exception("Invalid port config")
            self._no_interface_id_overlap_validation(th, service, fabric)

        except Exception as e:
            self.log.error(e)
            raise
        return _ncs.OK

    def _no_interface_id_overlap_validation(self, th, port, fabric):
        '''
        :th: ncs.maapi.Transaction
        :port: ncs.maagic.ListElement
        :fabric: fabric name string
        '''
        current_interface_id = self._get_interface_id(th, port)
        self._check_no_interface_id_overlap(
            th, current_interface_id, port, fabric)

    def _get_interface_id(self, th, port):
        '''
        :th: ncs.maapi.Transaction
        :port: ncs.maagic.ListElement
        '''
        interface_id = defaultdict(set)
        if port.port_type == 'ethernet':
            node = port.ethernet.node
            interface_id[node] = {id for id in port.ethernet.node_port}
        elif port.port_type == 'port-channel':
            node = port.port_channel.node
            interface_id[node] = {id for id in port.port_channel.node_port}
        elif port.port_type == 'vpc-port-channel':
            node_1, node_2 = utils.get_vpc_nodes_from_port(
                ncs.maagic.get_root(th), port)
            interface_id[node_1], interface_id[node_2] = {id for id in port.vpc_port_channel.node_1_port}, {
                id for id in port.vpc_port_channel.node_2_port}
        return interface_id

    def _check_no_interface_id_overlap(self, th, current_interface_id, current_port, fabric):
        '''
        :th: ncs.maapi.Transaction
        :current_interface_id: default dict object
        :current_port: ncs.maagic.ListElement
        :fabric: fabric name string
        '''
        root = ncs.maagic.get_root(th)
        port_configs = root.cisco_dc__dc_site[fabric].port_configs
        for port_group in port_configs:
            for port in port_group.port_config:
                if port.name != current_port.name:
                    if port.port_type == 'ethernet':
                        node = port.ethernet.node
                        node_port = {id for id in port.ethernet.node_port}
                        if current_interface_id.get(node):
                            if current_interface_id[node].intersection(node_port):
                                raise Exception(
                                    f'Interface id is already used for port {port.name}')
                    elif port.port_type == 'port-channel':
                        node = port.port_channel.node
                        node_port = {
                            id for id in port.port_channel.node_port}
                        if current_interface_id.get(node):
                            if current_interface_id[node].intersection(node_port):
                                raise Exception(
                                    f'Interface id is already used for port {port.name}')
                    elif port.port_type == 'vpc-port-channel':
                        node_1, node_2 = utils.get_vpc_nodes_from_port(
                            ncs.maagic.get_root(th), port)
                        node_1_port, node_2_port = {id for id in port.vpc_port_channel.node_1_port}, {
                            id for id in port.vpc_port_channel.node_2_port}
                        if current_interface_id.get(node_1):
                            if current_interface_id[node_1].intersection(node_1_port):
                                raise Exception(
                                    f'Interface id is already used for port {port.name}')
                        if current_interface_id.get(node_2):
                            if current_interface_id[node_2].intersection(node_2_port):
                                raise Exception(
                                    f'Interface id is already used for port {port.name}')
