import ncs
import l1access.create_functions as create_functions
import l1access.validate_functions as validate_functions
from collections import defaultdict


def l1_fabric_service(root, l1access, tctx, log):
    """Function to configure port service

    Args:
        root: Maagic object pointing to the root of the CDB
        l1access: service node
        tctx: transaction context (TransCtxRef)
        log: log object (self.log)

    """
    port_parameters = defaultdict()

    log.info(f'Configure Service {l1access.name}')
    create_functions.create_port_parameters(
        root, l1access, tctx, port_parameters, log)
    validate_functions.validate(
        port_parameters, ncs.maagic.get_trans(root), log)
    create_functions.create_port(l1access, port_parameters)
