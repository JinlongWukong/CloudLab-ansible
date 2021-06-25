from .container import Container


class Jenkins(Container):

    def create(self):
        """
        Jenkins specified create method, will parse initialAdminPassword
        :return: container status(address, port_mapping, initial admin password), data format -> dict
        """
        callback = self._create()

        for event in callback.host_ok:
            if event['task'] == "Get jenkins initialAdminPassword" and event['host'] == self.host_ip:
                self.initialAdminPassword = event['result']['stdout']
            else:
                pass

        return {
            "address": self.address,
            "port_mapping": self.port_mapping,
            "admin_password": self.initialAdminPassword
        }

    def get(self):
        """Get jenkins status information

         return: container status(address, port_mapping, initialAdminPassword), dict format
         """
        callback = self._get()

        for event in callback.host_ok:
            if event['task'] == "Get jenkins initialAdminPassword" and event['host'] == self.host_ip:
                self.initialAdminPassword = event['result']['stdout']
            else:
                pass

        return {
            "address": self.address,
            "port_mapping": self.port_mapping,
            "admin_password": self.initialAdminPassword
        }
