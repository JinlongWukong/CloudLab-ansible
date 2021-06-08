from ansible_task_executor import AnsibleTaskExecutor
import os


class HOST(object):

    def __init__(self, ip, user, password, subnet="192.168.122.0/24", role=None):
        self.ip = ip
        self.user = user
        self.password = password
        self.role = role
        self.cpu = None
        self.memory = None
        self.disk = None
        self.os_type = None
        self.subnet = subnet
        self.ansible_inventory = "{} ansible_ssh_user={} ansible_ssh_pass={}".format(ip, user, password)
        self.executor = AnsibleTaskExecutor()
        self.proxy = os.getenv('https_proxy')

    def install(self):
        result_code, callback = self.executor.execute('install-host.yml', self.ansible_inventory,
                                                      extra_vars={"role": self.role,
                                                                  "proxy_env": {'https_proxy': self.proxy},
                                                                  "subnet": self.subnet
                                                                  })
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

    def static_routes(self, routes):
        result_code, callback = self.executor.execute('route.yml', self.ansible_inventory,
                                                      extra_vars={"routes": routes})
        if result_code:
            raise Exception(callback.get_all_result())

    def get_info(self):
        """
            Get host cpu/mem/disk usage
        :return:
            cpu, mem, disk
        """
        result_code, callback = self.executor.execute('check-host.yml', self.ansible_inventory)

        if result_code:
            raise Exception(callback.get_all_result())

        for event in callback.host_ok:
            if event['task'] == "Print total memory avail" and event['host'] == self.ip:
                memory_avail = event['result']['msg']
            elif event['task'] == "Print cpu load usage" and event['host'] == self.ip:
                cpu_load = event['result']['msg']
            elif event['task'] == "Print virt vol disk usage" and event['host'] == self.ip:
                disk_usage = event['result']['msg']
            else:
                pass

        return memory_avail, cpu_load, disk_usage

    def port_dnat(self, rules):
        """
            Set iptables rules
        :return:
            none
        """
        result_code, callback = self.executor.execute('iptables.yml', self.ansible_inventory,
                                                      extra_vars={"rules": rules})
        if result_code:
            raise Exception(callback.get_all_result())


class MultiHOST(HOST):
    def __init__(self, hosts):
        self.ansible_inventory = ""
        for h in hosts:
            if len(h) != 3:
                continue
            self.ansible_inventory += "{} ansible_ssh_user={} ansible_ssh_pass={}".format(h[0], h[1], h[2]) + "\n"
        self.executor = AnsibleTaskExecutor()
