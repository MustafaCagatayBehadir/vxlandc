import ncs
from ncs.dp import Action


class ResourcePoolsAction(ncs.dp.Action):

    @Action.action
    def cb_action(self, uinfo, name, kp, input, output, trans):
        """Action to create resource pools for the site

        Parameters:
            uinfo: UserInfo object
            name: The tailf:action name
            kp: Keypath of the action
            action_input: Action input
            output: Action output
        """
        with ncs.maapi.single_write_trans('admin', 'python') as t:
            root = ncs.maagic.get_root(t)
            create_site_resource_pools(input, root, self.log)
            try:
                t.apply()
            except:
                output.success = False
            else:
                output.success = True


def create_site_resource_pools(input, root, log):
    """Function to create site resource pools

    Args:
        input: Action input
        root: Maagic object pointing to the root of the CDB
        log: log object (self.log)

    """
    site = root.cisco_dc__dc_site[input.site]
    # Standalone nodes
    nodes = [node for node in site.node if node.node_role !=
             'spine' and node.node_type != 'vpc']
    # vpc node groups
    node_groups = [node_group for node_group in site.node_group]
    for id_pool in input.id_pool:
        start, end = id_pool.start, id_pool.end
        if id_pool.scope.string == 'fabric':
            pool_name = f'{input.site}::{id_pool.id}'
            pool_parameters = {'Pool Name': pool_name,
                               'Start': start, 'End': end}
            log.info("ID Pool Parameters Dictionary: ",
                     pool_parameters)
            create_resource_pool(root, pool_parameters, log)
            create_resource_pool_reference(
                site, pool_parameters.get('Pool Name'), id_pool.scope.string)
        elif id_pool.scope.string == 'local':
            for node in nodes:
                pool_parameters = {
                    'Pool Name': f'{input.site}::{node.hostname}::{id_pool.id}', 'Start': start, 'End': end}
                log.info(
                    "ID Pool Parameters Dictionary: ", pool_parameters)
                create_resource_pool(root, pool_parameters, log)
                create_resource_pool_reference(
                    node, pool_parameters.get('Pool Name'), id_pool.scope.string)
            for node_group in node_groups:
                pool_name = f'{input.site}::{node_group.node_1}_{node_group.node_2}_VPC-{node_group.id}::{id_pool.id}'
                pool_parameters = {
                    'Pool Name': pool_name, 'Start': start, 'End': end}
                log.info(
                    "ID Pool Parameters Dictionary: ", pool_parameters)
                create_resource_pool(root, pool_parameters, log)
                create_resource_pool_reference(
                    node_group, pool_parameters.get('Pool Name'), id_pool.scope.string)


def create_resource_pool(root, pool_parameters, log):
    """Function to create resource pool

    Args:
        root: Maagic object pointing to the root of the CDB
        pool_parameters: Pool parameter dictionary
        log: log object (self.log)

    """
    id_pool = root.ralloc__resource_pools.idalloc__id_pool
    if pool_parameters.get('Pool Name') is not None and pool_parameters.get('Pool Name') not in id_pool:
        pool = id_pool.create(pool_parameters.get('Pool Name'))
        pool.range.start, pool.range.end = pool_parameters.get(
            'Start'), pool_parameters.get('End')
    else:
        log.info(f"Skipping pool create {pool_parameters.get('Pool Name')}")


def create_resource_pool_reference(node, pool_name, scope):
    """Function to create resource pool reference

    Args:
        node: Maagic object pointing to /dc-site/node | /dc-site/node-group | /dc-site
        pool_name: Resource id pool name
        scope: String. Can be fabric | local

    """
    if scope == 'local':
        node.po_id_pool = pool_name
    elif scope == 'fabric':
        resource_pool = node.resource_pools
        if 'l2-network-vlan' in pool_name:
            resource_pool.l2_network_vlan = pool_name
        elif 'fabric-external-l3-vrf-vlan' in pool_name:
            resource_pool.fabric_external_l3_vrf_vlan = pool_name
        elif 'l3-vrf-vlan' in pool_name:
            resource_pool.l3_vrf_vlan = pool_name
        elif 'l2-vxlan-vni' in pool_name:
            resource_pool.l2_vxlan_vni = pool_name
        elif 'l3-vxlan-vni' in pool_name:
            resource_pool.l3_vxlan_vni = pool_name


class BridgeDomainRedeployAction(ncs.dp.Action):
    @Action.action
    def cb_action(self, uinfo, name, kp, input, output, trans):
        """Action to re-deploy bridge domains attached to the port-configs

        Parameters:
            uinfo: UserInfo object
            name: The tailf:action name
            kp: Keypath of the action
            action_input: Action input
            output: Action output
        """
        self.log.info(f'Action is activated via kicker action {name}')
        kp_list = list()
        create_action_parameters(input, trans, kp_list, self.log)
        redeploy_bridge_domains(kp_list, name, self.log)
        self.log.info(f'Action is finished via kicker action {name}')


def create_action_parameters(input, trans, kp_list, log):
    """Function to create keypaths list of bridge domains attached to the port-configs

    Parameters:
        action_input: Action input
        trans: Transaction backend
        kp_list: Bridge-domain keypaths list
        log: log object (self.log)

    """
    monitor_node = ncs.maagic.get_node(trans, input.path)
    port_configs = monitor_node._parent
    for kp in port_configs.attached_bridge_domain_kp:
        kp_list.append(kp)
    log.info(
        f'Port configs {port_configs.name} attached bridge-domain kp list: {kp_list}')


def redeploy_bridge_domains(kp_list, name, log):
    """Function to redeploy bridge domains attached to the port-configs

    Parameters:
        kp_list: Bridge-domain keypaths list
        name: The tailf:action name
        log: log object (self.log)

    """
    with ncs.maapi.single_write_trans('admin', 'python') as t:
        for kp in kp_list:
            try:
                bd = ncs.maagic.get_node(t, kp)
                bd.touch()
            except KeyError:
                log.error(f'Bridge-domain {kp} can not be found.')
            else:
                log.info(f'Bridge-domain {bd.name} is activated via kicker action {name}')
        t.apply()