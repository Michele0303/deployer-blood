import yaml

from ssh_manager import SSHManager
from docker_manager import DockerManager


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
        config['ssh']['password'])
    try:
        ssh_manager.connect()
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    try:
        docker_manager = DockerManager(ssh_manager)
        services_info = docker_manager.setup_and_zip_services()

        for service in services_info:
            output, error = ssh_manager.execute_command(
                f'curl -F "chat_id={chat_id}" -F "document=@{service}" '
                f'"https://api.telegram.org/bot{token}/sendDocument"'
            )
            print(error)

    finally:
        ssh_manager.disconnect()


if __name__ == "__main__":
    main()
