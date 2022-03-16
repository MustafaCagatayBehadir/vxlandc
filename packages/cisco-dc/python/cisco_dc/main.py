# -*- mode: python; python-indent: 4 -*-
import ncs

from . import dc_actions

# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        
        ############################################################################################

        # DC-ACTIONS
        self.register_action('create-site-resource-pools', dc_actions.ResourcePoolsAction)

    def teardown(self):
        self.log.info('Main FINISHED')
