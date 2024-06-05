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
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print(f"Unable to connect to {self.hostname}: {e}")
            raise ConnectionError(e)

    def disconnect(self):
        if self.client:
            self.client.close()

    def execute_command(self, command):
        if self.client is None:
            raise ValueError("Connection not established.")

        try:
            print(f"[-] Run {command}")
            stdin, stdout, stderr = self.client.exec_command(command)
            return stdout.read().decode(), stderr.read().decode()
        except Exception as e:
            print(f"Failed to execute command {command}: {e}")

    def setup_environment(self):
        command = f"echo {self.password} | sudo -S apt install -y zip"
        self.client.execute_command(command)
