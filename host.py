from ansible_task_executor import AnsibleTaskExecutor


class HOST(object):

    def __init__(self, ip, user, password, role=None):
        self.ip = ip
        self.user = user
        self.password = password
        self.role = role
        self.cpu = None
        self.memory = None
        self.disk = None
        self.os_type = None
        self.ansible_inventory = "{} ansible_ssh_user={} ansible_ssh_pass={}".format(ip, user, password)
        self.executor = AnsibleTaskExecutor()

    def install(self):
        result_code, callback = self.executor.execute('install-host.yml', self.ansible_inventory,
                                                      extra_vars={"role": self.role})
        if result_code:
            raise Exception(callback.get_all_result())

        for event in callback.host_ok:
            if event['task'] == "Print total memory size" and event['host'] == self.ip:
                self.memory = event['result']['msg']
            elif event['task'] == "Print total cpu count" and event['host'] == self.ip:
                self.cpu = event['result']['msg']
            elif event['task'] == "Print os type" and event['host'] == self.ip:
                self.os_type = event['result']['msg']
            elif event['task'] == "Print virt vol disk usage" and event['host'] == self.ip:
                self.disk = int(event['result']['msg'])
            else:
                pass

        return self.cpu, self.memory, self.disk, self.os_type

    def get_info(self):
        """
            Get host latest information
        :return:
            cpu, mem, disk
        """
        result_code, callback = self.executor.execute('check-host.yml', self.ansible_inventory)

        if result_code:
            raise Exception(callback.get_all_result())

