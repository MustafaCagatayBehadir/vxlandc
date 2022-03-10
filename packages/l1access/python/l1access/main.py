# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import NanoService
import l1access.id_allocations as id_allocations
import l1access.configuration_functions as configure


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class NanoServiceCallbacks(NanoService):

    @NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state,
                       proplist, component_proplist):
        '''Nano service create callback'''
        self.log.info('Nano create(state=', state, ')')

        # State functions
        if state == 'l1access:id-allocated':
            id_allocations.id_requested(root, service, tctx, self.log)

        elif state == 'l1access:l1-fabric-service-configured':
            configure.l1_fabric_service(root, service, tctx, self.log)

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        # L1 ACCESS NANO PLAN
        self.register_nano_service('l1-fabric-service-servicepoint',
                                   'ncs:self', 'l1access:id-allocated', NanoServiceCallbacks)
        
        self.register_nano_service('l1-fabric-service-servicepoint', 'ncs:self',
                                   'l1access:l1-fabric-service-configured', NanoServiceCallbacks)
        

    def teardown(self):
        self.log.info('Main FINISHED')
