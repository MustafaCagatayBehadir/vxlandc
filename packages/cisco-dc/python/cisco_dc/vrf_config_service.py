from multiprocessing import connection
import ncs
from .resource_manager import id_allocator
from . import utils
from . import vrf_l3out_routing


class VrfServiceSelfComponent(ncs.application.NanoService):
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

        elif state == 'cisco-dc:vrf-configured':
            _configure_vrf(root, service, tctx, self.log)
            _apply_template(service)

        elif state == 'cisco-dc:vrf-l3out-routing-configured':
            vrf_l3out_routing._configure_l3out_routing(
                root, service, tctx, self.log)
            vrf_l3out_routing._apply_template(service)


def _id_requested(root, vrf, tctx, log):
    """Function to request vlan id & vni id from resource manager

    Args:
        root: Maagic object pointing to the root of the CDB
        vrf: service node
        tctx: transaction context (TransCtxRef)
        log: log object(self.log)
    """
    resource_pools = root.cisco_dc__dc_site[vrf.site].resource_pools
    id = [(vrf.l3vni.vlan_id if vrf.l3vni.vlan_id else -1, resource_pools.l3_vrf_vlan),
          (vrf.l3vni.vni_id if vrf.l3vni.vni_id else -1, resource_pools.l3_vxlan_vni),
          (vrf.l3vni.fabric_external_vlan_id if vrf.l3vni.fabric_external_vlan_id else -1, resource_pools.fabric_external_l3_vrf_vlan)]
    for requested_id, pool_name in id:
        svc_xpath = "/cisco-dc:dc-site[fabric='{}']/vrf-config[name='{}']"
        svc_xpath = svc_xpath.format(vrf.site, vrf.name)
        allocation_name = f'{vrf.site}:{vrf.name}'
        id_allocator.id_request(
            vrf, svc_xpath, tctx.username, pool_name, allocation_name, False, requested_id)
        log.info(
            f'Id is requested from pool {pool_name} for service {vrf.name}')


def _configure_vrf(root, vrf, tctx, log):
    """Function to configure vrf service

    Args:
        root: Maagic object pointing to the root of the CDB
        vrf: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    id_parameters = dict()
    _create_service_parameters(root, vrf, tctx, id_parameters, log)
    _raise_service_exceptions(root, vrf, tctx, id_parameters, log)
    _create_operational_lists(root, vrf, log)
    _set_hidden_leaves(root, vrf, id_parameters, log)


def _create_service_parameters(root, vrf, tctx, id_parameters, log):
    """Function to create vlan parameters and bd parameters

    Args:
        root: Maagic object pointing to the root of the CDB
        vrf: service node
        id_parameters: dict object
        log: log object (self.log)

    """
    resource_pools = root.cisco_dc__dc_site[vrf.site].resource_pools
    id = [('vrf-vlan', resource_pools.l3_vrf_vlan),
          ('l3vni', resource_pools.l3_vxlan_vni),
          ('fabric-external-vrf-vlan', resource_pools.fabric_external_l3_vrf_vlan)]
    for parameter, pool_name in id:
        allocation_name = f'{vrf.site}:{vrf.name}'
        id_parameters[parameter] = id_allocator.id_read(
            tctx.username, root, pool_name, allocation_name)
    log.info('Id Parameters :', id_parameters)


def _raise_service_exceptions(root, vrf, tctx, id_parameters, log):
    """Function to raise exception based on service prechecks

    Args:
        root: Maagic object pointing to the root of the CDB
        vrf: service node
        tctx: transaction context (TransCtxRef)
        id_parameters: dict object
        log: log object(self.log)

    """
    site = root.cisco_dc__dc_site[vrf.site]
    nodes = [
        node.hostname for node in site.node if node.node_role == 'border-leaf']
    connections = [site.connections.uplink_to_dci_gw_01,
                   site.connections.uplink_to_dci_gw_02]
    node_connections = [(node, connection)
                        for node in nodes for connection in connections]
    encap = id_parameters.get('fabric-external-vrf-vlan')
    for node, connection in node_connections:
        device = root.ncs__devices.device[node]
        if f'{connection}.{encap}' in device.config.nx__interface.port_channel:
            raise Exception(
                f'Fabric external vrf vlan {encap} is already used in device {node} connection port-channel{connection}.{encap}')


def _create_operational_lists(root, vrf, log):
    """Function to create operational lists

    Args:
        root: Maagic object pointing to the root of the CDB
        vrf: service node
        log: log object (self.log)

    """
    for kp in vrf.attached_bridge_domain_kp:
        try:
            bd = ncs.maagic.cd(root, kp)
            vrf.attached_bridge_domain.create(
                bd.site, bd.tenant, bd.name)
        except KeyError:
            log.error(f'Bridge-domain {kp} can not be found.')
        else:
            log.info(
                f'Vrf {vrf.name} attached bridge domain operational list is created for tenant {bd.tenant} bridge-domain {bd.name}')


def _set_hidden_leaves(root, vrf, id_parameters, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        vrf: service node
        id_parameters: dict object
        log: log object (self.log)

    """
    vrf.vlan_id, vrf.vni_id, vrf.fabric_external_vlan_id = id_parameters[
        'vrf-vlan'], id_parameters['l3vni'], id_parameters['fabric-external-vrf-vlan']

    site = root.cisco_dc__dc_site[vrf.site]
    border_leaves = [
        node.hostname for node in site.node if node.node_role == 'border-leaf']

    for kp in vrf.attached_bridge_domain_kp:
        try:
            bd = ncs.maagic.cd(root, kp)
            [vrf.device.create(kp, device.leaf_id) for device in bd.device]
        except KeyError:
            raise Exception(
                f'Bridge-domain {kp} can not be found.')
        else:
            log.info(
                f'Vrf {vrf.name} device is updated with bridge-domain {bd.name} keypath.')

    for leaf_id in border_leaves:
        vrf.device.create(vrf._path, leaf_id)
        log.info(
            f'Vrf {vrf.name} device is updated with border-leaf switches.')

    if vrf.direct.exists():
        if vrf.direct.address_family_ipv4_policy:
            dc_route_policies = root.cisco_dc__dc_site[vrf.site].dc_route_policy
            for dc_route_policy in dc_route_policies:
                if vrf.direct.address_family_ipv4_policy in dc_route_policy.route_policy:
                    route_policy = dc_route_policy.route_policy[vrf.direct.address_family_ipv4_policy]
                    route_policy.attached_vrf_kp.create(vrf._path)
                    log.info(
                        f'Dc route policy {dc_route_policy.name} route policy {route_policy.profile} attached vrf keypath leaf-list is updated by vrf {vrf.name}.')

        if vrf.direct.address_family_ipv6_policy:
            dc_route_policies = root.cisco_dc__dc_site[vrf.site].dc_route_policy
            for dc_route_policy in dc_route_policies:
                if vrf.direct.address_family_ipv6_policy in dc_route_policy.route_policy:
                    route_policy = dc_route_policy.route_policy[vrf.direct.address_family_ipv6_policy]
                    route_policy.attached_vrf_kp.create(vrf._path)
                    log.info(
                        f'Dc route policy {dc_route_policy.name} route policy {route_policy.profile} attached vrf keypath leaf-list is updated by vrf {vrf.name}.')

    if vrf.static.exists():
        if vrf.static.address_family_ipv4_policy:
            dc_route_policies = root.cisco_dc__dc_site[vrf.site].dc_route_policy
            for dc_route_policy in dc_route_policies:
                if vrf.static.address_family_ipv4_policy in dc_route_policy.route_policy:
                    route_policy = dc_route_policy.route_policy[vrf.static.address_family_ipv4_policy]
                    route_policy.attached_vrf_kp.create(vrf._path)
                    log.info(
                        f'Dc route policy {dc_route_policy.name} route policy {route_policy.profile} attached vrf keypath leaf-list is updated by vrf {vrf.name}.')

        if vrf.static.address_family_ipv6_policy:
            dc_route_policies = root.cisco_dc__dc_site[vrf.site].dc_route_policy
            for dc_route_policy in dc_route_policies:
                if vrf.static.address_family_ipv6_policy in dc_route_policy.route_policy:
                    route_policy = dc_route_policy.route_policy[vrf.static.address_family_ipv6_policy]
                    route_policy.attached_vrf_kp.create(vrf._path)
                    log.info(
                        f'Dc route policy {dc_route_policy.name} route policy {route_policy.profile} attached vrf keypath leaf-list is updated by vrf {vrf.name}.')


def _apply_template(vrf):
    """Function to create vrf configuration

    Args:
        vrf: service node

    """
    template = ncs.template.Template(vrf)
    vars = ncs.template.Variables()
    vars.add('VLAN_NAME', utils.get_vrf_vlan_name(vrf))
    template.apply('cisco-dc-services-fabric-bd-l3vni-service', vars)
