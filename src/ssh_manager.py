import logging

import paramiko


class SSHManager:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname=self.hostname,
                                username=self.username,
                                password=self.password)
            self.setup_environment()
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print(f"Unable to connect to {self.hostname}: {e}")
            raise ConnectionError(e)

    def disconnect(self):
        if self.client:
            self.client.close()

    def execute_command(self, command):
        if self.client is None:
            raise ValueError("Connection not established.")

        logging.info(f"Executing command: {command}")

        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()

    def setup_environment(self):
        command = "sudo -S apt install -y zip"
        stdin, stdout, stderr = self.client.exec_command(command)
        stdin.write(self.password + "\n")
        stdin.flush()
        return stdout.read().decode(), stderr.read().decode()
