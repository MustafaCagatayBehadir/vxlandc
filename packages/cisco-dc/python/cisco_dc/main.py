# -*- mode: python; python-indent: 4 -*-
import ncs

from . import dc_actions
from . import port_config_service
from . import validate_callback

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------


class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')

        # Port Config Registration
        self.register_nano_service('port-config-servicepoint', 'ncs:self',
                                   'cisco-dc:id-allocated', port_config_service.PortServiceSelfComponent)

        self.register_nano_service('port-config-servicepoint', 'ncs:self',
                                   'cisco-dc:port-configured', port_config_service.PortServiceSelfComponent)

        # Port Config Service  Validation
        self.port_config_val = validate_callback.ValPointRegistrar(
            self.log, 'port-config-val', 'port-config-service-validation', port_config_service.PortConfigServiceValidator(self.log))
        ############################################################################################

        # DC-ACTIONS
        self.register_action('create-site-resource-pools',
                             dc_actions.ResourcePoolsAction)

    def teardown(self):
        self.log.info('Main FINISHED')
