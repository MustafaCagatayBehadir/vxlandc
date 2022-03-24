import ncs
from ncs.experimental import Query


def validate(port_parameters, trans, log):
    """Parent function for all validations

    Args:
        port_parameters: port configuration elements dictionary
        trans: Read/Write transaction, same as action transaction if executed with a service context. (maapi.Transaction)
        log: log object(self.log)

    """
    is_port_used(port_parameters, trans, log)


def is_port_used(port_parameters, trans, log):
    """Function to validate port is not used by another service

    Args:
        port_parameters: port configuration elements dictionary
        trans: Read/Write transaction, same as action transaction if executed with a service context. (maapi.Transaction)
        log: log object(self.log)

    """
    log.info(f'Start to validate for port {port_parameters["name"]}...')
    if port_parameters['type'] == 'ethernet':
        query_is_port_used(
            port_parameters['name'], port_parameters['node'], port_parameters['node-port'], trans, log)
    elif port_parameters['type'] == 'port-channel':
        query_is_port_used(
            port_parameters['name'], port_parameters['node'], port_parameters['node-port'], trans, log)
    elif port_parameters['type'] == 'vpc-port-channel':
        query_is_port_used(
            port_parameters['name'], port_parameters['node-1'], port_parameters['node-1-port'], trans, log)
        query_is_port_used(
            port_parameters['name'], port_parameters['node-2'], port_parameters['node-2-port'], trans, log)


def query_is_port_used(port_name, node, node_port, trans, log):
    """Function to query port and raise exception if it is used by another service

    Args:
        port_name: port name ex. PC100001
        node: node name port is resides on
        node_port: port id list ex. [1/1, 1/2]
        trans: Read/Write transaction, same as action transaction if executed with a service context. (maapi.Transaction)
        log: log object(self.log)

    """
    for port_id in node_port:
        query_path = "/ncs:devices/ncs:device[ncs:name='{}']/ncs:config/nx:interface/nx:Ethernet[nx:name='{}']".format(
            node, port_id)
        with Query(trans, query_path, '/', ['description'], result_as=ncs.QUERY_STRING) as q:
            for r in q:
                if r[0]:
                    raise Exception(
                        f"Node {node} ethernet port {port_id} is already used")
    log.info(f'Validation is finished for port {port_name}...')
