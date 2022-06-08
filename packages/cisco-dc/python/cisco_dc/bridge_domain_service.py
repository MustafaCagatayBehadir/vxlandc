import ncs
import _ncs
import ncs.maapi as maapi
import ncs.maagic as maagic

from .resource_manager import id_allocator
from . import bridge_domain_l3out_routing
from . import utils
from . import xrapi
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address, IPv4Network


class BridgeDomainServiceCallback(ncs.application.Service):
    @ncs.application.Service.pre_modification
    def cb_pre_modification(self, tctx, op, kp, root, proplist):

        self.log.info(
            "ENTRY_POINT for {} at pre_mod of BridgeDomainConfigService, operation: {}" .format(
                utils.get_kp_service_id(kp),
                utils.get_service_operation(op)))
        try:
            if op == _ncs.dp.NCS_SERVICE_CREATE:
                m = maapi.Maapi()
                th = m.attach(tctx)

                bd = maagic.get_node(th, str(kp))
                # raise Exception("invalid create operation")
                self._is_prefix_used(bd, proplist)

            elif op == _ncs.dp.NCS_SERVICE_UPDATE:
                m = maapi.Maapi()
                th = m.attach(tctx)

                bd = maagic.get_node(th, str(kp))
                # raise Exception("invalid update operation")
                self._is_prefix_used(bd, proplist)

        except Exception as e:
            self.log.error(e)
            raise
        self.log.info('Proplist: ', proplist)

        return []

    @ncs.application.Service.pre_modification
    def cb_post_modification(self, tctx, op, kp, root, proplist):

        self.log.info(
            "ENTRY_POINT for {} at post_mod of BridgeDomainConfigService, operation: {}" .format(
                utils.get_kp_service_id(kp),
                utils.get_service_operation(op)))

        try:
            m = maapi.Maapi()
            th = m.attach(tctx)

            bd = maagic.get_node(th, str(kp))
            self._refill_proplist(bd, proplist)
            self.log.info('Proplist: ', proplist)

        except KeyError:
            self.log.error(f'Bridge-domain {str(kp)} can not be found.')

        return proplist

    def _refill_proplist(self, bd, proplist):
        """Function to create proplist at the post modification

        Args:
            bd: service node
            proplist: properties (list(tuple(str, str)), structure to pass data between callbacks

        """
        index = 0
        for bd_subnet in bd.bd_subnet:
            if bd_subnet.address_family == 'ipv4':
                index += 1
                proplist.append((str(index), bd_subnet.address))

        routing = bd.routing
        if routing.static_route.exists():
            static_route = routing.static_route
            for destination in static_route.destination:
                ip = destination.address
                if type(ip_network(ip)) is IPv4Network:
                    index += 1
                    proplist.append((str(index), ip))

    def _is_prefix_used(self, bd, proplist):
        """Function to check if prefix is already used in the network

        Args:
            bd: service node
            proplist: properties (list(tuple(str, str)), structure to pass data between callbacks

        """
        self.log.info('Route check is started...')
        for bd_subnet in bd.bd_subnet:
            ip = utils.getIpAddress(bd_subnet.address)
            if type(ip_address(ip)) is IPv4Address and bd_subnet.address not in proplist:
                self.log.info(f'Prefix {bd_subnet.address} is checking...')
            else:
                self.log.info(
                    f'Skipping prefix {bd_subnet.address} because it is already checked.')


class BridgeDomainServiceSelfComponent(ncs.application.NanoService):
    """
    NanoService callback handler for the self component of bridge-domain service.
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
            _apply_template(service)

        elif state == 'cisco-dc:bridge-domain-l3out-routing-configured':
            bridge_domain_l3out_routing._configure_l3out_routing(
                root, service, tctx, self.log)
            bridge_domain_l3out_routing._apply_template(service)

        self.log.info('Proplist: ', proplist)

        return []


def _id_requested(root, bd, tctx, log):
    """Function to request vlan id & vni id from resource manager

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        tctx: transaction context (TransCtxRef)
        log: log object(self.log)
    """
    resource_pools = root.cisco_dc__dc_site[bd.site].resource_pools
    id = [(bd.l2vni.vlan_id if bd.l2vni.vlan_id else -1, resource_pools.l2_network_vlan),
          (bd.l2vni.vni_id if bd.l2vni.vni_id else -1, resource_pools.l2_vxlan_vni)]
    for requested_id, pool_name in id:
        svc_xpath = "/cisco-dc:dc-site[fabric='{}']/tenant-service[name='{}']/bridge-domain[name='{}']"
        svc_xpath = svc_xpath.format(bd.site, bd.tenant, bd.name)
        allocation_name = f'{bd.site}:{bd.tenant}:{bd.name}'
        id_allocator.id_request(
            bd, svc_xpath, tctx.username, pool_name, allocation_name, False, requested_id)
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
          ('l2vni', resource_pools.l2_vxlan_vni)]
    for parameter, pool_name in id:
        allocation_name = f'{bd.site}:{bd.tenant}:{bd.name}'
        id_parameters[parameter] = id_allocator.id_read(
            tctx.username, root, pool_name, allocation_name)
    log.info('Id Parameters :', id_parameters)


def _set_hidden_leaves(root, bd, id_parameters, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        id_parameters: dict object
        log: log object (self.log)

    """
    bd.vlan_id, bd.vni_id = id_parameters.values()
    port_groups = root.cisco_dc__dc_site[bd.site].port_configs
    attached_port_groups = bd.port_group
    for attached_port_group in attached_port_groups:
        port_group = port_groups[attached_port_group.name]
        ports = port_group.port_config
        if (bd._path) not in port_group.bd_service:
            port_group.bd_service.create(bd._path)
        for port in ports:
            if port.type == 'ethernet':
                if utils.is_node_vpc(root, port):
                    node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
                    if (port._path, node_1) not in bd.device:
                        bd.device.create(port._path, node_1)
                    if (port._path, node_2) not in bd.device:
                        bd.device.create(port._path, node_2)
                else:
                    eth = port.ethernet
                    node = eth.node
                    if (port._path, node) not in bd.device:
                        bd.device.create(port._path, node)

            elif port.type == 'port-channel':
                if utils.is_node_vpc(root, port):
                    node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
                    if (port._path, node_1) not in bd.device:
                        bd.device.create(port._path, node_1)
                    if (port._path, node_2) not in bd.device:
                        bd.device.create(port._path, node_2)
                else:
                    pc = port.port_channel
                    node = pc.node
                    if (port._path, node) not in bd.device:
                        bd.device.create(port._path, node)

            elif port.type == 'vpc-port-channel':
                vpc = port.vpc_port_channel
                node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
                if (port._path, node_1) not in bd.device:
                    bd.device.create(port._path, node_1)
                if (port._path, node_2) not in bd.device:
                    bd.device.create(port._path, node_2)

            log.info(
                f'Port {port.name} bridge-bomain {bd.name} hidden configuration is applied.')

    for bd_subnet in bd.bd_subnet:
        ip = utils.getIpAddress(bd_subnet.address)
        bd_subnet.address_family = "ipv4" if type(
            ip_address(ip)) is IPv4Address else "ipv6"

    if bd.vrf:
        vrf = root.cisco_dc__dc_site[bd.site].vrf_config[bd.vrf]
        for device in bd.device:
            if (bd._path, device.leaf_id) not in vrf.bd_device:
                vrf.bd_device.create(bd._path, device.leaf_id)
        log.info(f'Vrf {bd.vrf} is activated by bridge-domain {bd.name}')


def _apply_template(bd):
    """Function to apply configurations to devices

    Args:
        bd: service node

    """
    template = ncs.template.Template(bd)
    vars = ncs.template.Variables()
    vars.add('VLAN_NAME', utils.get_network_vlan_name(bd))
    vars.add('DESCRIPTION', utils.get_svi_description(bd))
    template.apply('cisco-dc-services-fabric-bd-vlan-service', vars)
    template.apply('cisco-dc-services-fabric-bd-l2vni-service', vars)


class BridgeDomainServiceValidator(object):
    def __init__(self, log):
        self.log = log

    def cb_validate(self, tctx, kp, newval):
        '''
        Validating bridge-domain bd-subnet list has at least one primary ipv4 address
        '''

        try:
            self.log.debug("Validating bridge-domain service")
            m = maapi.Maapi()
            th = m.attach(tctx)

            service = maagic.get_node(th, str(kp))

            # raise Exception("Invalid bridge-domain config")
            self._bd_subnet_validation(th, service)

        except Exception as e:
            self.log.error(e)
            raise
        return _ncs.OK

    def _bd_subnet_validation(self, th, bd):
        '''
        :th: ncs.maapi.Transaction
        :bd: ncs.maagic.ListElement
        '''
        if bd.vrf:
            flag_ipv4, num_preferred_address = False, 0
            for bd_subnet in bd.bd_subnet:
                ip = utils.getIpAddress(bd_subnet.address)
                if type(ip_address(ip)) is IPv4Address:
                    flag_ipv4 = True
                    if bd_subnet.preferred.string == 'yes':
                        num_preferred_address += 1
                if type(ip_address(ip)) is IPv6Address:
                    if bd_subnet.preferred.string == 'yes':
                        raise Exception(
                            f'Bridge-Domain {bd.name} bd-subnet {bd_subnet.address} should not be selected as preferred address.')
            if flag_ipv4 and num_preferred_address < 1:
                raise Exception(
                    f'Bridge-Domain {bd.name} has at least one preferred IPv4 subnet.')
            elif flag_ipv4 and num_preferred_address > 1:
                raise Exception(
                    f'Bridge-Domain {bd.name} should not have more than one preferred IPv4 subnet.')
