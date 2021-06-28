from .container import Container


class Mysql(Container):

    def create(self):
        """
        Mysql specified create method, will get root password
        :return: container status(address, port_mapping, root password), data format -> dict
        """
        self.callback = self._create()
        self.read_root_password()

        return {
            "status": self.status,
            "address": self.address,
            "port_mapping": self.port_mapping,
            "additional_infor": {"root_password": self.root_passwd} if self.root_passwd else {}
        }

    def get(self):
        """Get jenkins status information

         return: container status, address, port_mapping, format dict
         """
        self.callback = self._get()
        self.read_root_password()

        return {
            "status": self.status,
            "address": self.address,
            "port_mapping": self.port_mapping,
            "additional_infor": {"root_password": self.root_passwd} if self.root_passwd else {}
        }

    def read_root_password(self):
        """
        Read mysql root password
        """
        self.root_passwd = ""
        for event in self.callback.host_ok:
            if event['task'] == "Get mysql root password" and event['host'] == self.host_ip:
                self.root_passwd = event['result']['stdout']
            else:
                pass
