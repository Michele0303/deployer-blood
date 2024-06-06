import logging
import paramiko


class SSHManager:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()

    def connect(self):
        try:
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

    def execute_command_as_root(self, command):
        if self.client is None:
            raise ValueError("Connection not established.")

        command = "sudo -S -p '' %s" % command
        logging.info(f"Executing command: {command}")

        stdin, stdout, stderr = self.client.exec_command(command=command)
        stdin.write(self.password + "\n")
        stdin.flush()

        stdoutput = [line for line in stdout]
        stderroutput = [line for line in stderr]
        for output in stdoutput:
            logging.info("Job: %s" % (output.strip()))

        return stdoutput, stderroutput

    def setup_environment(self):
        self.execute_command_as_root('apt update')
        self.execute_command_as_root('apt install -y curl zip')
