import l2access.create_functions as create_functions


def id_requested(root, l2access, tctx, log):
    """Function to allocate vlan id & vni id

    Args:
        root: Maagic object pointing to the root of the CDB
        l2access: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    Returns:
        None
    """
    create_functions.allocate_vlan_id(root, l2access, tctx, log)
    create_functions.allocate_vni_id(root, l2access, tctx, log)
