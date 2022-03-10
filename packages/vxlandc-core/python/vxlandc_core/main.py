# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service
from vxlandc_core.resource_pools import ResourcePools


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_action('create-site-resource-pools', ResourcePools)

    def teardown(self):
        self.log.info('Main FINISHED')
