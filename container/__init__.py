from .jenkins import Jenkins
from .mysql import Mysql


class ContainerFactory(object):
    @staticmethod
    def new_container(host_ip, host_user, host_pass, name, cpus, memory, container_type, version):
        if container_type == 'jenkins':
            return Jenkins(host_ip, host_user, host_pass, name, cpus, memory, container_type, version)
        elif container_type == 'mysql':
            return Mysql(host_ip, host_user, host_pass, name, cpus, memory, container_type, version)
        else:
            raise TypeError("Unknown container type")
