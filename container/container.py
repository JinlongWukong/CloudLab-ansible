from ansible_task_executor import AnsibleTaskExecutor


class Container(object):

    def __init__(self, host_ip, host_user, host_pass, name, cpus, memory, container_type, version):
        self.host_ip = host_ip
        self.name = name
        self.container_type = container_type
        self.cpus = cpus
        self.memory = memory
        self.version = version
        self.address = None
        self.port_mapping = []
        self.status = "unknown"
        self.ansible_inventory = "{} ansible_ssh_user={} ansible_ssh_pass={}".format(host_ip, host_user, host_pass)
        self.executor = AnsibleTaskExecutor()

    def _create(self):
        """
        Internal common create method, create container, parse address and port_mapping
        :return: ansible callback
        """
        result_code, callback = self.executor.execute('container.yml', self.ansible_inventory,
                                                      extra_vars={"container_type": self.container_type,
                                                                  "container_name": self.name,
                                                                  "tag": self.version,
                                                                  "memory_limit": self.memory,
                                                                  "cpu_limit": self.cpus
                                                                  },
                                                      tags=['create'])
        if result_code:
            raise Exception(callback.get_failed_result())

        for event in callback.host_ok:
            if event['task'] == "Create container" and event['host'] == self.host_ip:
                if 'container existed' in event['result']['stdout']:
                    raise Exception("Container {} already existed".format(self.name))
            else:
                self.read_container_status(event)

        return callback

    def create(self):
        """Create container

        return: container status(address, port_mapping), dict format
        """
        self._create()

        return {
            "status": self.status,
            "address": self.address,
            "port_mapping": self.port_mapping
        }

    def start(self):
        """Start container

        return: container status(address, port_mapping), dict format
        Raises: if ansible failed, raise error message
        """
        result_code, callback = self.executor.execute('container.yml', self.ansible_inventory,
                                                      extra_vars={"container_name": self.name,
                                                                  "container_type": self.container_type},
                                                      tags=['start'])
        if result_code:
            raise Exception(callback.get_failed_result())

        for event in callback.host_ok:
            self.read_container_status(event)

        return {
            "status": self.status,
            "address": self.address,
            "port_mapping": self.port_mapping,
            "additional_infor": {}
        }

    def restart(self):
        """Restart container

        return: container status(address, port_mapping), dict format
        Raises: if ansible failed, raise error message
        """
        result_code, callback = self.executor.execute('container.yml', self.ansible_inventory,
                                                      extra_vars={"container_name": self.name,
                                                                  "container_type": self.container_type},
                                                      tags=['restart'])
        if result_code:
            raise Exception(callback.get_failed_result())

        for event in callback.host_ok:
            self.read_container_status(event)

        return {
            "status": self.status,
            "address": self.address,
            "port_mapping": self.port_mapping,
            "additional_infor": {}
        }

    def stop(self):
        """Stop container

        return: None
        Raises: if ansible failed, raise error message
        """
        result_code, callback = self.executor.execute('container.yml', self.ansible_inventory,
                                                      extra_vars={"container_name": self.name},
                                                      tags=['stop'])
        if result_code:
            raise Exception(callback.get_failed_result())

    def delete(self):
        """Delete container

        return: None
        Raises: if ansible failed, raise error message
        """
        result_code, callback = self.executor.execute('container.yml', self.ansible_inventory,
                                                      extra_vars={"container_name": self.name},
                                                      tags=['delete'])
        if result_code:
            raise Exception(callback.get_failed_result())

    def _get(self):
        """Internal common get container status information

        return: ansible callback
        """
        result_code, callback = self.executor.execute('container.yml', self.ansible_inventory,
                                                      extra_vars={"container_name": self.name,
                                                                  "container_type": self.container_type},
                                                      tags=['get'])
        if result_code:
            raise Exception(callback.get_failed_result())

        for event in callback.host_ok:
            self.read_container_status(event)

        return callback

    def get(self):
        """Get container status information

        return: container status, address, port_mapping, format dict
        """
        self._get()

        return {
            "status": self.status,
            "address": self.address,
            "port_mapping": self.port_mapping,
            "additional_infor": {}
        }

    def read_container_status(self, event):
        """
        This is a common method for reading container status information
        """
        if event['task'] == "Check container liveness" and event['host'] == self.host_ip:
            if 'container is up' in event['result']['stdout']:
                self.status = "running"
            elif 'container is down' in event['result']['stdout']:
                self.status = "stopped"
            elif 'container is missing' in event['result']['stdout']:
                self.status = "deleted"
            else:
                self.status = "unknown"
        elif event['task'] == "Get container ip address" and event['host'] == self.host_ip:
            self.address = event['result']['stdout']
        elif event['task'] == "Get container port mapping" and event['host'] == self.host_ip:
            self.port_mapping = event['result']['stdout_lines']
        else:
            pass
