from .container import Container


class Postgres(Container):

    def create(self):
        """
        Postgres specified create method
        :return: container status(address, port_mapping, postgres password), data format -> dict
        """
        self.callback = self._create()
        self.get_postgres_password()

        return {
            "status": self.status,
            "address": self.address,
            "port_mapping": self.port_mapping,
            "additional_infor": dict({"postgres_password": self.postgres_passwd})
        }

    def get_postgres_password(self):
        """
        Read postgres password
        """
        self.postgres_passwd = ""
        for event in self.callback.host_ok:
            if event['task'] == "Print random password" and event['host'] == self.host_ip:
                self.postgres_passwd = event['result']['msg']
            else:
                pass
