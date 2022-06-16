import ncs
import _ncs
import ncs.maapi as maapi
import ncs.maagic as maagic

import json

from .resource_manager import id_allocator
from .xrapi import Xrapi
from . import bridge_domain_l3out_routing
from . import utils
from ipaddress import ip_address, ip_network, IPv4Address, IPv6Address, IPv4Network


class BridgeDomainServiceCallback(ncs.application.Service):
    @ncs.application.Service.pre_modification
    def cb_pre_modification(self, tctx, op, kp, root, proplist):

        self.log.info(
            "ENTRY_POINT for {} at pre_mod of BridgeDomainConfigService, operation: {}" .format(
                utils.get_kp_service_id(kp),
                utils.get_service_operation(op)))
        try:
            new_proplist = list()
            if op == _ncs.dp.NCS_SERVICE_CREATE:
                m = maapi.Maapi()
                th = m.attach(tctx)

                bd = maagic.get_node(th, str(kp))

                self._create_new_proplist(bd, new_proplist)
                # raise Exception("invalid create operation")
                self._is_prefix_used(root, bd, proplist, new_proplist)

            elif op == _ncs.dp.NCS_SERVICE_UPDATE:
                m = maapi.Maapi()
                th = m.attach(tctx)

                bd = maagic.get_node(th, str(kp))

                self._create_new_proplist(bd, new_proplist)
                # raise Exception("invalid update operation")
                self._is_prefix_used(root, bd, proplist, new_proplist)

        except Exception as e:
            self.log.error(e)
            raise

        return proplist if proplist == new_proplist else new_proplist

    def _create_new_proplist(self, bd, new_proplist):
        """Function to create new proplist for bridge-domain

        Args:
            bd: service node
            new_proplist: new properties (list(tuple(str, str)) structure

        """
        new_route_ref = [bd_subnet.address for bd_subnet in bd.bd_subnet if type(
            ip_address(utils.getIpAddress(bd_subnet.address))) is IPv4Address]

        if bd.routing:
            routing = bd.routing
            if routing.static_route.exists():
                static_route = routing.static_route
                for destination in static_route.destination:
                    ip = destination.address
                    if type(ip_network(ip)) is IPv4Network:
                        new_route_ref.append(ip)

        # Fill new proplist
        new_proplist.append((bd.name, json.dumps(new_route_ref)))

    def _is_prefix_used(self, root, bd, proplist, new_proplist):
        """Function to check if prefix is already used in the network

        Args:
            root: Maagic object pointing to the root of the CDB
            bd: service node
            proplist: properties (list(tuple(str, str)), structure to pass data between callbacks
            new_proplist: new properties (list(tuple(str, str)) structure

        """
        self.log.info('Route check is started...')
        cmd_list = utils.get_cmd_dict_from_bd(root, bd, proplist, new_proplist)
        
        dci = root.cisco_dc__dc_site[bd.site].fabric_parameters.dci_reference
        username, password = utils.get_basic_authentication(root, dci.authgroup)
        
        if cmd_list:
            xrapi = Xrapi(dci.address, username, password, self.log)
            xrapi.send_show_commands(bd, cmd_list)


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
            _id_allocated(root, service, tctx, self.log)

        elif state == 'cisco-dc:bridge-domain-configured':
            _configure_bridge_domain(root, service, tctx, self.log)
            _apply_template(service)

        elif state == 'cisco-dc:bridge-domain-l3out-routing-configured':
            bridge_domain_l3out_routing._configure_l3out_routing(
                root, service, tctx, self.log)
            bridge_domain_l3out_routing._apply_template(service)

        self.log.info('Proplist: ', proplist)

        return proplist


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


def _id_allocated(root, bd, tctx, log):
    """Function to read vlan and vni ids from resource manager and set id_allocated leaf for the next state

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        tctx: transaction context (TransCtxRef)
        log: log object(self.log)

    """
    resource_pools = root.cisco_dc__dc_site[bd.site].resource_pools
    id = [('network-vlan', resource_pools.l2_network_vlan),
          ('l2vni', resource_pools.l2_vxlan_vni)]
    for parameter, pool_name in id:
        allocation_name = f'{bd.site}:{bd.tenant}:{bd.name}'
        if id_allocator.id_read(tctx.username, root, pool_name, allocation_name):
            bd.id_allocated = True
        else:
            bd.id_allocated = False
            break


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
    log.info('Bridge Domain Config Id Parameters :', id_parameters)


def _set_hidden_leaves(root, bd, id_parameters, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        bd: service node
        id_parameters: dict object
        log: log object (self.log)

    """
    bd.vlan_id, bd.vni_id = id_parameters.values()
    port_configs = root.cisco_dc__dc_site[bd.site].port_configs
    for port_group in bd.port_group:
        port_config = port_configs[port_group.name].port_config
        for port in port_config:
            if port.type == 'ethernet':
                if utils.is_node_vpc(root, port):
                    node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
                    bd.device.create(port._path, node_1)
                    bd.device.create(port._path, node_2)
                else:
                    eth = port.ethernet
                    node = eth.node
                    bd.device.create(port._path, node)

            elif port.type == 'port-channel':
                if utils.is_node_vpc(root, port):
                    node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
                    bd.device.create(port._path, node_1)
                    bd.device.create(port._path, node_2)
                else:
                    pc = port.port_channel
                    node = pc.node
                    bd.device.create(port._path, node)

            elif port.type == 'vpc-port-channel':
                node_1, node_2 = utils.get_vpc_nodes_from_port(root, port)
                bd.device.create(port._path, node_1)
                bd.device.create(port._path, node_2)

            log.info(
                f'Port {port.name} bridge-bomain {bd.name} hidden configuration is applied.')

        port_configs[port_group.name].attached_bridge_domain.create(
            bd.site, bd.tenant, bd.name)
        port_configs[port_group.name].attached_bridge_domain_kp.create(
            bd._path)
        log.info(
            f'Port configs {port_group.name} attached bridge domain operational list is updated by tenant {bd.tenant} bridge-domain {bd.name}.')

    for bd_subnet in bd.bd_subnet:
        ip = utils.getIpAddress(bd_subnet.address)
        bd_subnet.address_family = "ipv4" if type(
            ip_address(ip)) is IPv4Address else "ipv6"

    if bd.vrf:
        vrf = root.cisco_dc__dc_site[bd.site].vrf_config[bd.vrf]
        bd_device = vrf.bd_device.create(bd._path)
        for device in bd.device:
            bd_device.leaf_id.create(device.leaf_id)
        log.info(
            f'Vrf {bd.vrf} attached bridge domain device list is updated by tenant {bd.tenant} bridge-domain {bd.name}.')


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
