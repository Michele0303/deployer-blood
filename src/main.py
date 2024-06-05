import yaml
import logging

from ssh_manager import SSHManager
from docker_manager import DockerManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(path="../config/config.yaml"):
    with open(path, 'r') as file:
        return yaml.safe_load(file)


def main():
    config = load_config()

    token = config['telegram']['token']
    chat_id = config['telegram']['chat_id']

    ssh_manager = SSHManager(
        config['ssh']['hostname'],
        config['ssh']['username'],
        config['ssh']['password']
    )

    try:
        ssh_manager.connect()

        docker_manager = DockerManager(ssh_manager)
        services_info = docker_manager.setup_and_zip_services()

        for service in services_info:
            ssh_manager.execute_command(
                f'curl -F "chat_id={chat_id}" -F "document=@{service}" '
                f'"https://api.telegram.org/bot{token}/sendDocument"')
    finally:
        ssh_manager.disconnect()


if __name__ == "__main__":
    main()
