import l1access.create_functions as create_functions


def id_requested(root, port, tctx, log):
    """Function to allocate port-channel id

    Args:
        root: Maagic object pointing to the root of the CDB
        port: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    Returns:
        None
    """
    create_functions.allocate_po_id(root, port, tctx, log)
