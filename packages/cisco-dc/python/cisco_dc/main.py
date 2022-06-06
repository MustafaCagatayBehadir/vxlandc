# -*- mode: python; python-indent: 4 -*-
import ncs

from . import dc_actions
from . import port_config_service
from . import bridge_domain_service
from . import vrf_config_service
from . import dc_routepolicy
from . import tenant_service
from . import validate_callback

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------


class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')

        # Port Config Premod
        self.register_service('port-config-servicepoint',
                              port_config_service.PortServiceCallback)

        # Port Config Registration
        self.register_nano_service('port-config-servicepoint', 'ncs:self',
                                   'cisco-dc:id-allocated', port_config_service.PortServiceSelfComponent)

        self.register_nano_service('port-config-servicepoint', 'ncs:self',
                                   'cisco-dc:port-configured', port_config_service.PortServiceSelfComponent)

        # Bridge Domain Registration
        self.register_nano_service('bridge-domain-config-servicepoint', 'ncs:self',
                                   'cisco-dc:id-allocated', bridge_domain_service.BridgeDomainServiceSelfComponent)

        self.register_nano_service('bridge-domain-config-servicepoint', 'ncs:self',
                                   'cisco-dc:bridge-domain-configured', bridge_domain_service.BridgeDomainServiceSelfComponent)

        self.register_nano_service('bridge-domain-config-servicepoint', 'ncs:self',
                                   'cisco-dc:bridge-domain-l3out-routing-configured', bridge_domain_service.BridgeDomainServiceSelfComponent)

        # Bridge Domain Service Validation
        self.port_config_val = validate_callback.ValPointRegistrar(
            self.log, 'bridge-domain-val', 'bridge-domain-service-validation', bridge_domain_service.BridgeDomainServiceValidator(self.log))

        # VRF Config Registration
        self.register_nano_service('vrf-config-servicepoint', 'ncs:self',
                                   'cisco-dc:id-allocated', vrf_config_service.VrfServiceSelfComponent)

        self.register_nano_service('vrf-config-servicepoint', 'ncs:self',
                                   'cisco-dc:vrf-configured', vrf_config_service.VrfServiceSelfComponent)

        self.register_nano_service('vrf-config-servicepoint', 'ncs:self',
                                   'cisco-dc:vrf-l3out-routing-configured', vrf_config_service.VrfServiceSelfComponent)

        # Route Policy Registration
        self.register_service('route-policy-config-servicepoint',
                              dc_routepolicy.RoutePolicyConfigService)

        # Tenant Service Validation
        self.tenant_service_val = validate_callback.ValPointRegistrar(
            self.log, 'tenant-service-val', 'tenant-service-validation', tenant_service.TenantServiceValidator(self.log))
        ############################################################################################

        # DC-ACTIONS
        self.register_action('create-site-resource-pools',
                             dc_actions.ResourcePoolsAction)

    def teardown(self):
        self.log.info('Main FINISHED')
