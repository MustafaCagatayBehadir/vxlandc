# -*- mode: python; python-indent: 4 -*-
import ncs

from . import dc_actions
from . import port_config_service
from . import bridge_domain_service
from . import vrf_config_service
from . import dc_routepolicy
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

        # Port Config Service Validation
        self.port_config_val = validate_callback.ValPointRegistrar(
            self.log, 'port-config-val', 'port-config-service-validation', port_config_service.PortConfigServiceValidator(self.log))

        # Bridge Domain Registration
        self.register_nano_service('bridge-domain-config-servicepoint', 'ncs:self',
                                   'cisco-dc:id-allocated', bridge_domain_service.BridgeDomainServiceSelfComponent)

        self.register_nano_service('bridge-domain-config-servicepoint', 'ncs:self',
                                   'cisco-dc:bridge-domain-configured', bridge_domain_service.BridgeDomainServiceSelfComponent)

        # VRF Config Registration
        self.register_nano_service('vrf-config-servicepoint', 'ncs:self',
                                   'cisco-dc:id-allocated', vrf_config_service.VrfServiceSelfComponent)

        self.register_nano_service('vrf-config-servicepoint', 'ncs:self',
                                   'cisco-dc:vrf-configured', vrf_config_service.VrfServiceSelfComponent)

        # Route Policy Registration
        self.register_service('route-policy-config-servicepoint',
                              dc_routepolicy.RoutePolicyConfigService)

        ############################################################################################

        # DC-ACTIONS
        self.register_action('create-site-resource-pools',
                             dc_actions.ResourcePoolsAction)

    def teardown(self):
        self.log.info('Main FINISHED')
