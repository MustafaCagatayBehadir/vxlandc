import ncs
import _ncs
import ncs.maapi as maapi
import ncs.maagic as maagic
from collections import defaultdict
import re


from . import utils
from .resource_manager import id_allocator


class PortServiceCallback(ncs.application.Service):
    @ncs.application.Service.pre_modification
    def cb_pre_modification(self, tctx, op, kp, root, proplist):

        self.log.info(
            "ENTRY_POINT for {} at pre_mod of PortConfigService, operation: {}" .format(
                utils.get_kp_service_id(kp),
                utils.get_service_operation(op)))

        if op == _ncs.dp.NCS_SERVICE_CREATE:
            try:
                m = maapi.Maapi()
                th = m.attach(tctx)
                port = maagic.get_node(th, str(kp))
                disable_validation = root.cisco_dc__dc_site[port.site].validations.disable_port_config_validation
                if not disable_validation.exists():
                    # raise Exception("invalid create operation")
                    self._is_port_used(root, port)

            except Exception as e:
                self.log.error(e)
                raise

            else:
                self._redeploy_bridge_domains(root, port, kp, th, self.log)

        elif op == _ncs.dp.NCS_SERVICE_UPDATE:
            try:
                m = maapi.Maapi()
                th = m.attach(tctx)
                port = maagic.get_node(th, str(kp))
                disable_validation = root.cisco_dc__dc_site[port.site].validations.disable_port_config_validation
                if not disable_validation.exists():
                    # raise Exception("invalid update operation")
                    self._is_port_used(root, port)

            except Exception as e:
                self.log.error(e)
                raise

        elif op == _ncs.dp.NCS_SERVICE_DELETE:
            try:
                with ncs.maapi.single_write_trans('admin', 'python') as th:
                    port = maagic.get_node(th, str(kp))
                    disable_validation = root.cisco_dc__dc_site[
                        port.site].validations.disable_port_config_validation
                    if not disable_validation.exists():
                        # raise Exception("invalid update operation")
                        self._is_port_down(root, port)

            except KeyError as e:
                self.log.error(e)

            except Exception as e:
                self.log.error(e)
                raise

            else:
                m = maapi.Maapi()
                th = m.attach(tctx)
                self._redeploy_bridge_domains(root, port, kp, th, self.log)

    def _is_port_down(self, root, port):
        """Function to check port physical state

        Args:
            root: Maagic object pointing to the root of the CDB
            port: Service node

        """
        if port.port_type == 'ethernet':
            eth = port.ethernet
            device = root.ncs__devices.device[eth.node]
            result = utils.send_show_command(
                device, 'interface status | json-pretty', self.log)
            for node_port in eth.node_port:
                for interface in result['TABLE_interface']['ROW_interface']:
                    if interface['interface'] == f'Ethernet{node_port}':
                        if interface['state'] == 'connected':
                            raise Exception(
                                f'Port {port.name} state is connected, port can not be deleted.')
                        else:
                            break

        elif port.port_type == 'port-channel':
            pc = port.port_channel
            device = root.ncs__devices.device[pc.node]
            result = utils.send_show_command(
                device, 'interface status | json-pretty', self.log)
            for interface in result['TABLE_interface']['ROW_interface']:
                if interface['interface'] == f'port-channel{pc.allocated_port_channel_id}':
                    if interface['state'] == 'connected':
                        raise Exception(
                            f'Port {port.name} state is connected, port can not be deleted.')
                    else:
                        break

        elif port.port_type == 'vpc-port-channel':
            vpc = port.vpc_port_channel
            for node in vpc.node:
                device = root.ncs__devices.device[node.name]
                result = utils.send_show_command(
                    device, 'interface status | json-pretty', self.log)
                for interface in result['TABLE_interface']['ROW_interface']:
                    if interface['interface'] == f'port-channel{vpc.allocated_port_channel_id}':
                        if interface['state'] == 'connected':
                            raise Exception(
                                f'Port {port.name} state is connected, port can not be deleted.')
                        else:
                            break

    def _is_port_used(self, root, port):
        """Function to check if port is manually configured

        Args:
            root: Maagic object pointing to the root of the CDB
            port: Service node

        """
        if port.port_type == 'ethernet':
            eth = port.ethernet
            node_port = eth.node_port
            device = root.ncs__devices.device[eth.node]
            ethernet = device.config.nx__interface.Ethernet
            for _port in node_port:
                if not ethernet[_port].enable.switchport:
                    raise Exception(
                        f'Switch {eth.node} port {_port} is not a switchport.')

                if ethernet[_port].description:
                    if port.description:
                        if ethernet[_port].description != port.description:
                            raise Exception(
                                f'Switch {eth.node} port {_port} has a different description.')
                    else:
                        if ethernet[_port].description != utils.get_description(port):
                            raise Exception(
                                f'Switch {eth.node} port {_port} has a different description.')

        elif port.port_type == 'port-channel':
            pc = port.port_channel
            node_port = pc.node_port
            device = root.ncs__devices.device[pc.node]
            ethernet = device.config.nx__interface.Ethernet
            for _port in node_port:
                if not ethernet[_port].enable.switchport:
                    raise Exception(
                        f'Switch {pc.node} port {_port} is not a switchport.')

                if ethernet[_port].description:
                    if ethernet[_port].description != utils.get_po_member_description(port):
                        raise Exception(
                            f'Switch {pc.node} port {_port} has a different description.')

        else:
            node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
            vpc_nodes = [(node_1, port.vpc_port_channel.node_1_port),
                         (node_2, port.vpc_port_channel.node_2_port)]
            for node, node_port in vpc_nodes:
                device = root.ncs__devices.device[node]
                ethernet = device.config.nx__interface.Ethernet
                for _port in node_port:
                    if not ethernet[_port].enable.switchport:
                        raise Exception(
                            f'Switch {node} port {_port} is not a switchport.')

                    if ethernet[_port].description:
                        if ethernet[_port].description != utils.get_po_member_description(port):
                            raise Exception(
                                f'Switch {node} port {_port} has a different description.')

    def _redeploy_bridge_domains(self, root, port, kp, th, log):
        """Function to redeploy bridge domains attached to the port-configs

        Args:
            root: Maagic object pointing to the root of the CDB
            port: Service node
            kp: Service node keypath object
            th: Transaction backend
            log: Log object (self.log)

        """
        pg_kp = re.match(r'(\.*\/.*)\/(.*)', str(kp)).groups()[0]
        try:
            port_configs = ncs.maagic.get_node(th, pg_kp)
        except KeyError:
            log.error(f'Port group {pg_kp} can not be found.')
        else:
            for kp in port_configs.attached_bridge_domain_kp:
                try:
                    bd = ncs.maagic.cd(root, kp)
                    bd.touch()
                except KeyError:
                    log.error(f'Bridge-domain {kp} can not be found.')
                else:
                    log.info(
                        f'Tenant {bd.tenant} bridge-domain {bd.name} is touched by port {port.name}')


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
            _id_allocated(root, service, tctx, self.log)

        elif state == 'cisco-dc:port-configured':
            _configure_port(root, service, tctx, self.log)
            _apply_template(service)


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


def _id_allocated(root, port, tctx, log):
    """Function to read port-channel id from resource manager and set id_allocated leaf for the next state

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        tctx: transaction context (TransCtxRef)
        log: log object(self.log)

    """
    if port.port_type == 'port-channel':
        if id_allocator.id_read(
                tctx.username, root, utils.get_port_channel_id_pool_name(root, port), f'{port.site}:{port.port_group}:{port.name}'):
            port.id_allocated = True
    elif port.port_type == 'vpc-port-channel':
        if id_allocator.id_read(
                tctx.username, root, utils.get_port_channel_id_pool_name(root, port), f'{port.site}:{port.port_group}:{port.name}'):
            port.id_allocated = True
    else:
        port.id_allocated = True


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
    _raise_service_exceptions(root, port, tctx, id_parameters, log)
    _set_hidden_leaves(root, port, tctx, id_parameters, log)


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
    log.info('Port Config Id Parameters: ', id_parameters)


def _raise_service_exceptions(root, port, tctx, id_parameters, log):
    """Function to raise exception based on service prechecks

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        tctx: transaction context (TransCtxRef)
        id_parameters: dict object
        log: log object(self.log)

    """
    disable_validation = root.cisco_dc__dc_site[port.site].validations.disable_port_config_validation
    if not disable_validation.exists():
        if port.port_type == 'port-channel':
            pc = port.port_channel
            device = root.ncs__devices.device[pc.node]
            po_id, port_channel = id_parameters['port-channel-id'], device.config.nx__interface.port_channel
            if po_id in port_channel and port_channel[po_id].description != utils.get_description(port):
                raise Exception(
                    f'Port-channel id {po_id} is already used in device {pc.node}.')

        elif port.port_type == 'vpc-port-channel':
            vpc_nodes = utils.get_vpc_nodes_from_port(root, port)
            for node in vpc_nodes:
                device = root.ncs__devices.device[node]
                po_id, port_channel = id_parameters['port-channel-id'], device.config.nx__interface.port_channel
                if po_id in port_channel and port_channel[str(po_id)].description != utils.get_description(port):
                    raise Exception(
                        f'Port-channel id {id_parameters["port-channel-id"]} is already used in device {node}.')


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
        port.ethernet.node_copy = port.ethernet.node
        [port.ethernet.node_port_copy.create(
            node_port) for node_port in port.ethernet.node_port]

    elif port.port_type == 'port-channel':
        port.type = 'port-channel'
        port.port_channel.node_copy = port.port_channel.node
        port.port_channel.allocated_port_channel_id = id_parameters.get(
            'port-channel-id')

    elif port.port_type == 'vpc-port-channel':
        port.type = 'vpc-port-channel'
        port.vpc_port_channel.node_group_copy = port.vpc_port_channel.node_group
        port.vpc_port_channel.allocated_port_channel_id = id_parameters.get(
            'port-channel-id')
        node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
        vpc_nodes = [(node_1, port.vpc_port_channel.node_1_port),
                     (node_2, port.vpc_port_channel.node_2_port)]
        for node, node_port in vpc_nodes:
            vpc_node = port.vpc_port_channel.node.create(node)
            vpc_node.node_port = node_port

    # Update attached-ports for kicker
    port_configs = root.cisco_dc__dc_site[port.site].port_configs[port.port_group]
    port_configs.attached_ports.create(port.name)

    port.auto_bum = utils.get_bum(port.speed)
    port.mode = port_configs.mode

    # Create vlan id list from bridge-domain keypath
    for kp in port_configs.attached_bridge_domain_kp:
        try:
            bd = ncs.maagic.cd(root, kp)
            port.vlan.create(bd.vlan_id)
        except KeyError:
            log.error(f'Bridge-domain {kp} can not be found.')
        else:
            log.info(
                f'Port {port.name} vlan id list is created for tenant {bd.tenant} bridge-domain {bd.name}')


def _apply_template(port):
    """Function to create port configuration

    Args:
        port: service node

    """
    vars = ncs.template.Variables()
    vars.add('DESCRIPTION',
             port.description if port.description else utils.get_description(port))
    vars.add('MEMBER_DESCRIPTION', utils.get_po_member_description(port))
    vars.add('BUM', float(port.bum) if port.bum else float(port.auto_bum))
    template = ncs.template.Template(port)
    template.apply('cisco-dc-services-fabric-port-service', vars)


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

            self.log.info('Port config service validation keypath: ', kp)
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
