import ncs


class DcRoutePolicyServiceCallback(ncs.application.Service):
    @ncs.application.Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')
        _create_route_map_config(service)
        

def _create_route_map_config(route_map):
    """Function to create route-map configuration

    Args:
        route-map: service node

    """
    template = ncs.template.Template(route_map)
    template.apply('cisco-dc-services-fabric-route-policy')