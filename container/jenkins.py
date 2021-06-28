from .container import Container


class Jenkins(Container):

    def create(self):
        """
        Jenkins specified create method, will parse initialAdminPassword
        :return: container status(address, port_mapping, initial admin password), data format -> dict
        """
        self.callback = self._create()
        self.read_admin_password()

        return {
            "status": self.status,
            "address": self.address,
            "port_mapping": self.port_mapping,
            "additional_infor": {"admin_password": self.initialAdminPassword} if self.initialAdminPassword else {}
        }

    def get(self):
        """Get jenkins status information

         return: container status, address, port_mapping, format dict
         """
        self.callback = self._get()
        self.read_admin_password()

        return {
            "status": self.status,
            "address": self.address,
            "port_mapping": self.port_mapping,
            "additional_infor": {"admin_password": self.initialAdminPassword} if self.initialAdminPassword else {}
        }

    def read_admin_password(self):
        """
        Read jenkins initial admin password
        """
        self.initialAdminPassword = ""
        for event in self.callback.host_ok:
            if event['task'] == "Get jenkins initialAdminPassword" and event['host'] == self.host_ip:
                self.initialAdminPassword = event['result']['stdout']
            else:
                pass
