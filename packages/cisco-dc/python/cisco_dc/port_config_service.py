import ncs

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
        svc_xpath = "/cisco-dc:dc-site[fabric='{}']/cisco-dc:port-configs/cisco-dc:port-config[cisco-dc:name='{}']"
        svc_xpath = svc_xpath.format(port.site, port.name)
        id_allocator.id_request(port, svc_xpath, tctx.username, utils.get_port_channel_id_pool_name(
            root, port), f'{port.site}::{port.name}', False, requested_id)
        log.info(f'Port-Channel id is requested for port {port.name}')
    elif port.port_type == 'vpc-port-channel':
        requested_id = port.vpc_port_channel.port_channel_id if port.vpc_port_channel.port_channel_id else -1
        svc_xpath = "/cisco-dc:dc-site[fabric='{}']/cisco-dc:port-configs/cisco-dc:port-config[cisco-dc:name='{}']"
        svc_xpath = svc_xpath.format(port.site, port.name)
        id_allocator.id_request(port, svc_xpath, tctx.username, utils.get_port_channel_id_pool_name(
            root, port), f'{port.site}::{port.name}', False, requested_id)
        log.info(f'Port-Channel id is requested for port {port.name}')


def _configure_port(root, port, tctx, log):
    """Function to configure port service

    Args:
        root: Maagic object pointing to the root of the CDB
        l1access: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    port_parameters = defaultdict()

    log.info(f'Configure Service {port.name}')
    _create_port_parameters(root, port, tctx, port_parameters, log)
    _create_port(port, port_parameters)


def _create_port_parameters(root, port, tctx, port_parameters, log):
    """Function to create port parameters for Ethernet & Port-Channel & VPC Port-Channel

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        tctx: transaction context (TransCtxRef)
        port_parameters: empty dict object
        log: log object(self.log)

    """
    port_parameters['name'] = port.name
    port_parameters['mode'] = port.mode.string
    port_parameters['speed'] = port.speed.string
    port_parameters['type'] = str(port.port_type)
    port_parameters['connection'] = port.connection.string
    port_parameters['shutdown'] = 'TRUE' if port.shutdown else 'FALSE'
    port_parameters['description'] = port.description if port.description else utils.get_description(
        port, port_parameters)
    port_parameters['bum'] = utils.get_bum(port_parameters)
    port_parameters['trap'] = 'TRUE' if port.speed.string != '1G' or port.storm_control_action_trap else 'FALSE'

    if port_parameters['type'] == 'ethernet':
        port_parameters['node'] = port.ethernet.node
        port_parameters['node-port'] = port.ethernet.node_port.as_list()
        port_parameters['vpc-node'] = 'TRUE' if utils.is_node_vpc(
            root, port, port_parameters) else 'FALSE'
    elif port_parameters['type'] == 'port-channel':
        port_parameters['port-channel-id'] = id_allocator.id_read(
            tctx.username, root, utils.get_port_channel_id_pool_name(root, port), f'{port.site}::{port.name}')
        port_parameters['node'] = port.port_channel.node
        port_parameters['node-port'] = port.port_channel.node_port.as_list()
        port_parameters['vpc-node'] = 'TRUE' if utils.is_node_vpc(
            root, port, port_parameters) else 'FALSE'
        port_parameters['is-vpc'] = 'FALSE'
    elif port_parameters['type'] == 'vpc-port-channel':
        port_parameters['port-channel-id'] = id_allocator.id_read(
            tctx.username, root, utils.get_port_channel_id_pool_name(root, port), f'{port.site}::{port.name}')
        port_parameters['node-1'], port_parameters['node-2'] = utils.get_vpc_nodes(
            root, port)
        port_parameters['node-1-port'] = port.vpc_port_channel.node_1_port.as_list()
        port_parameters['node-2-port'] = port.vpc_port_channel.node_2_port.as_list()
        port_parameters['vpc-node'] = 'TRUE'
        port_parameters['is-vpc'] = 'TRUE'

    log.info('Port Parameters: ', port_parameters)

    # Set hidden elements
    _set_hidden_leaves(port, port_parameters)

    # Create Node Port Flat Lists for Query
    _set_node_port_flat_leaf_list(port, port_parameters)


def _set_node_port_flat_leaf_list(port, port_parameters):
    """Function to set node-port-flat leaf-list for query operations

    Args:
        port: service node
        port_parameters: port configuration elements dictionary        

    """
    if port_parameters['type'] == 'ethernet':
        port.ethernet.node_port_flat = ",".join(
            [str(_port_id) for _port_id in port_parameters['node-port']])
    elif port_parameters['type'] == 'port-channel':
        port.port_channel.node_port_flat = ",".join(
            [str(_port_id) for _port_id in port_parameters['node-port']])
    elif port_parameters['type'] == 'vpc-port-channel':
        port.vpc_port_channel.node_1_port_flat = ",".join(
            [str(_port_id) for _port_id in port_parameters['node-1-port']])
        port.vpc_port_channel.node_2_port_flat = ",".join(
            [str(_port_id) for _port_id in port_parameters['node-2-port']])


def _set_hidden_leaves(port, port_parameters):
    """Function to set hidden leaves which are used for convenience

    Args:
        port: service node
        port_parameters: port configuration elements dictionary    

    """
    if port_parameters['type'] == 'ethernet':
        port.type = 'ethernet'
    elif port_parameters['type'] == 'port-channel':
        port.type = 'port-channel'
        port.port_channel.allocated_port_channel_id = port_parameters['port-channel-id']
    elif port_parameters['type'] == 'vpc-port-channel':
        port.type = 'vpc-port-channel'
        port.vpc_port_channel.allocated_port_channel_id = port_parameters['port-channel-id']


def _create_port(port, port_parameters):
    """Function to create port

    Args:
        port: service node
        port_parameters: port configuration elements dictionary
    """
    tvars = ncs.template.Variables()
    tvars.add('PORT_MODE', port_parameters['mode'])
    tvars.add('DESCRIPTION', port_parameters['description'])
    tvars.add('CONNECTION', port_parameters['connection'])
    tvars.add('BUM', port_parameters['bum'])
    tvars.add('VPC_NODE', port_parameters['vpc-node'])
    tvars.add('SHUTDOWN', port_parameters['shutdown'])
    tvars.add('TRAP', port_parameters['trap'])

    if port_parameters['type'] == 'ethernet':
        tvars.add('DEVICE', port_parameters['node'])
        for node_port in port_parameters['node-port']:
            tvars.add('ETH_ID', node_port)
            utils.apply_template(port, 'ethernet', tvars)
    elif port_parameters['type'] == 'port-channel':
        tvars.add('DEVICE', port_parameters['node'])
        tvars.add('PO_ID', port_parameters['port-channel-id'])
        tvars.add('VPC', port_parameters['is-vpc'])
        utils.apply_template(port, 'port-channel', tvars)
        for node_port in port_parameters['node-port']:
            tvars.add('ETH_ID', node_port)
            tvars.add('PO_MEMBER_DESCRIPTION', utils.get_po_member_description(
                node_port, port_parameters))
            utils.apply_template(port, 'port-channel-member', tvars)
    elif port_parameters['type'] == 'vpc-port-channel':
        tvars.add('PO_ID', port_parameters['port-channel-id'])
        tvars.add('VPC', port_parameters['is-vpc'])
        vpc_params = {port_parameters['node-1']: port_parameters['node-1-port'],
                      port_parameters['node-2']: port_parameters['node-2-port']}
        for node, node_ports in vpc_params.items():
            tvars.add('DEVICE', node)
            utils.apply_template(port, 'port-channel', tvars)
            for node_port in node_ports:
                tvars.add('ETH_ID', node_port)
                tvars.add('PO_MEMBER_DESCRIPTION', utils.get_po_member_description(
                    node_port, port_parameters))
                utils.apply_template(port, 'port-channel-member', tvars)
