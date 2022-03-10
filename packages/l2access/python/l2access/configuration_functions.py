import l2access.create_functions as create_functions
from collections import defaultdict


def l2_fabric_service(root, l2access, tctx, log):
    """Function to configure l2access service

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    vlan_trunking_parameters = defaultdict(dict)
    l2vni_parameters = defaultdict(dict)

    log.info(f'Configure Service {l2access.name}')
    create_functions.create_l2access_parameters(
        root, tctx, l2access, vlan_trunking_parameters, l2vni_parameters, log)
    create_functions.create_vlan(l2access, l2vni_parameters)
    create_functions.create_vlan_trunking(
        root, l2access, vlan_trunking_parameters)
