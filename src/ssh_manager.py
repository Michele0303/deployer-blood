import logging
from fabric import Connection, Config


class SSHManager:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password

        self.config = Config(overrides={'sudo': {'password': password}})
        self.client = None

    def connect(self):
        try:
            self.client = Connection(
                self.hostname, user=self.username, config=self.config, port=22,
                connect_kwargs={'password': self.password})

            self.setup_environment()
        except Exception as e:
            print(f"Unable to connect to {self.hostname}: {e}")
            raise ConnectionError(e)

    def execute_command(self, command):
        if self.client is None:
            raise ValueError("Connection not established.")

        logging.info(f"Executing command: {command}")

        return self.client.run(command)

    def execute_command_as_root(self, command):
        if self.client is None:
            raise ValueError("Connection not established.")

        return self.client.sudo(command)

    def setup_environment(self):
        self.execute_command_as_root('apt update -y')
        self.execute_command_as_root('apt install -y curl zip')
