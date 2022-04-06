import ncs


class DcRoutePolicySelfComponent(ncs.application.NanoService):
    """
    NanoService callback handler for the self component of route-policy service.
    """
    @ncs.application.NanoService.create
    def cb_nano_create(self, tctx, root, service, plan, component, state,
                       proplist, component_proplist):
        '''Nano service create callback'''
        self.log.info('Nano create(state=', state, ')')

        # State functions
        if state == 'cisco-dc:route-policy-configured':
            pass
