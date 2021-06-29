from ansible_task_executor import AnsibleTaskExecutor
import os


class K8S(object):

    def __init__(self, ip, user, password, controller_num=1, worker_num=3):
        self.ip = ip
        self.user = user
        self.password = password
        self.controller_num = controller_num
        self.worker_num = worker_num
        self.ansible_inventory = "{} ansible_ssh_user={} ansible_ssh_pass={}".format(ip, user, password)
        self.executor = AnsibleTaskExecutor()
        self.proxy = os.getenv('https_proxy')

    def install(self):
        result_code, callback = self.executor.execute('k8s.yml', self.ansible_inventory,
                                                      extra_vars={"control_plane_number": self.controller_num,
                                                                  "worker_number": self.worker_num,
                                                                  "proxy_env": {'https_proxy': self.proxy}
                                                                  })
        if result_code:
            raise Exception(callback.get_failed_result())

        return
