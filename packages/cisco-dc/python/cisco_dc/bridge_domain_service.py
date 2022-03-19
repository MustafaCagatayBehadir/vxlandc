import ncs
from .resource_manager import id_allocator


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
            _configure_tenant(root, service, tctx, self.log)


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
        log.info(f'Id is requested from pool {pool_name} for service {bd.name}')


def _configure_tenant(root, service, tctx, log):
    pass
