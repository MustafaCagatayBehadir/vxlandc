import ncs

import json


class PortGroupService(ncs.application.Service):

    @ncs.application.Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        new_proplist = list()
        _configure_port_group(root, service, proplist,
                              new_proplist, tctx, self.log)
        self.log.info('Proplist: ', proplist)
        self.log.info('New Proplist: ', new_proplist)

        return proplist if proplist == new_proplist else new_proplist


def _configure_port_group(root, port_group, proplist, new_proplist, tctx, log):
    """Function to configure port group service

    Args:
        root: Maagic object pointing to the root of the CDB
        port_group: service node
        proplist: properties (list(tuple(str, str)), structure to pass data between callbacks
        new_proplist: new properties (list(tuple(str, str)) structure
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    _create_new_proplist(root, port_group, new_proplist, tctx, log)
    _create_operational_lists(root, port_group, log)
    _set_hidden_leaves(root, port_group, proplist, new_proplist, log)


def _create_new_proplist(root, port_group, new_proplist, tctx, log):
    """Function to create new proplist

    Args:
        root: Maagic object pointing to the root of the CDB
        port_group: service node
        new_proplist: new properties (list(tuple(str, str)) structure
        log: log object (self.log)

    """
    port_config_ref = []
    for port_config in port_group.port_config:
        port_config_ref.append((port_config.kp, ','.join(port_config.node_port))) if hasattr(
            port_config, 'node_port') and port_config.node_port else port_config_ref.append((port_config.kp, ''))
    new_proplist.append((port_group.name, json.dumps(port_config_ref)))


def _create_operational_lists(root, port_group, log):
    """Function to create operational lists

    Args:
        root: Maagic object pointing to the root of the CDB
        port_group: service node
        log: log object (self.log)

    """
    for kp in port_group.attached_bridge_domain_kp:
        try:
            bd = ncs.maagic.cd(root, kp)
            port_group.attached_bridge_domain.create(
                bd.site, bd.tenant, bd.name)
        except KeyError:
            log.error(f'Bridge-domain {kp} can not be found.')
        else:
            log.info(
                f'Port group {port_group.name} attached bridge domain operational list is created for bridge-domain {bd.name}')


def _set_hidden_leaves(root, port_group, proplist, new_proplist, log):
    """Function to create hidden leaves for template operations

    Args:
        root: Maagic object pointing to the root of the CDB
        port_group: service node
        proplist: properties (list(tuple(str, str)), structure to pass data between callbacks
        new_proplist: new properties (list(tuple(str, str)) structure
        log: log object (self.log)

    """
    if proplist != new_proplist:
        for kp in port_group.attached_bridge_domain_kp:
            try:
                bd = ncs.maagic.cd(root, kp)
                id = bd.port_config_counter
                bd.port_config_counter = id + 1
            except KeyError:
                log.error(f'Bridge-domain {kp} can not be found.')
            else:
                log.info(
                    f'Bridge domain {bd.name} is updated by the port group service {port_group.name}.')
