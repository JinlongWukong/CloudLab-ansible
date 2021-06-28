from .jenkins import Jenkins
from .mysql import Mysql
from .postgres import Postgres
from .container import Container


class ContainerFactory(object):
    @staticmethod
    def new_container(host_ip, host_user, host_pass, name, cpus, memory, container_type, version):
        if container_type == 'jenkins':
            return Jenkins(host_ip, host_user, host_pass, name, cpus, memory, container_type, version)
        elif container_type == 'mysql':
            return Mysql(host_ip, host_user, host_pass, name, cpus, memory, container_type, version)
        elif container_type == 'postgres':
            return Postgres(host_ip, host_user, host_pass, name, cpus, memory, container_type, version)
        elif container_type in ['redis', 'mongodb', 'influxdb', 'prometheus', 'grafana']:
            return Container(host_ip, host_user, host_pass, name, cpus, memory, container_type, version)
        else:
            raise TypeError("Unknown container type")
