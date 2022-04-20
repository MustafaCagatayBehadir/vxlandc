import ncs
from .resource_manager import id_allocator


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
          (vrf.l3vni.vni_id if vrf.l3vni.vni_id else -1, resource_pools.l3_vxlan_vni)]
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
          ('l3vni', resource_pools.l3_vxlan_vni)]
    for parameter, pool_name in id:
        allocation_name = f'{vrf.site}:{vrf.name}'
        id_parameters[parameter] = id_allocator.id_read(
            tctx.username, root, pool_name, allocation_name)
    log.info('Id Parameters :', id_parameters)


def _set_hidden_leaves(root, vrf, id_parameters, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        vrf: service node
        id_parameters: dict object
        log: log object (self.log)

    """
    vrf.vlan_id, vrf.vni_id = id_parameters.values()
    if vrf.direct.exists():
        if vrf.direct.address_family_ipv4_policy:
            dc_route_policies = root.cisco_dc__dc_site[vrf.site].dc_route_policy
            for dc_route_policy in dc_route_policies:
                if vrf.direct.address_family_ipv4_policy in dc_route_policy.route_policy:
                    route_policy = dc_route_policy.route_policy[vrf.direct.address_family_ipv4_policy]
                    for device in vrf.device:
                        if (vrf._path, device.leaf_id) not in route_policy.device:
                            route_policy.device.create(
                                vrf._path, device.leaf_id)

        if vrf.direct.address_family_ipv6_policy:
            dc_route_policies = root.cisco_dc__dc_site[vrf.site].dc_route_policy
            for dc_route_policy in dc_route_policies:
                if vrf.direct.address_family_ipv6_policy in dc_route_policy.route_policy:
                    route_policy = dc_route_policy.route_policy[vrf.direct.address_family_ipv6_policy]
                    for device in vrf.device:
                        if (vrf.name, device.leaf_id) not in route_policy.device:
                            route_policy.device.create(
                                vrf._path, device.leaf_id)

    if vrf.static.exists():
        if vrf.static.address_family_ipv4_policy:
            dc_route_policies = root.cisco_dc__dc_site[vrf.site].dc_route_policy
            for dc_route_policy in dc_route_policies:
                if vrf.static.address_family_ipv4_policy in dc_route_policy.route_policy:
                    route_policy = dc_route_policy.route_policy[vrf.static.address_family_ipv4_policy]
                    for device in vrf.device:
                        if (vrf.name, device.leaf_id) not in route_policy.device:
                            route_policy.device.create(
                                vrf._path, device.leaf_id)

        if vrf.static.address_family_ipv6_policy:
            dc_route_policies = root.cisco_dc__dc_site[vrf.site].dc_route_policy
            for dc_route_policy in dc_route_policies:
                if vrf.static.address_family_ipv6_policy in dc_route_policy.route_policy:
                    route_policy = dc_route_policy.route_policy[vrf.static.address_family_ipv6_policy]
                    for device in vrf.device:
                        if (vrf.name, device.leaf_id) not in route_policy.device:
                            route_policy.device.create(
                                vrf._path, device.leaf_id)


def _apply_template(vrf):
    """Function to create vrf configuration

    Args:
        vrf: service node

    """
    template = ncs.template.Template(vrf)
    template.apply('cisco-dc-services-fabric-bd-l3vni-service')
