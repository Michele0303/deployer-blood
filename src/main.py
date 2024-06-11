import yaml
import logging

from ssh_manager import SSHManager
from docker_manager import DockerManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(path="../config/config.yaml"):
    with open(path, 'r') as file:
        return yaml.safe_load(file)


def get_service_ports_from_docker_ps(ssh_manager, service_name):
    command = f"docker ps --filter 'name={service_name}' --format '{{{{.Ports}}}}'"
    output = ssh_manager.execute_command(command).stdout.strip()

    # parse ports
    for entry in output.split(','):
        host_port = entry.split('->')[0].split(':')[1]
        return host_port


def service_process(ssh_manager, service) -> bool:

    with ssh_manager.client.cd(service):

        output = ssh_manager.execute_command(f"ls").stdout
        if 'docker-compose.yml' not in output:
            return False

        ssh_manager.execute_command('docker compose up -d')
        ssh_manager.execute_command('docker ps')

    port = get_service_ports_from_docker_ps(ssh_manager, service)
    logging.info(f"Ports for service {service}: {port}")



    return True


def main():
    config = load_config()

    token = config['telegram']['token']
    chat_id = config['telegram']['chat_id']

    services_dir = config['ssh']['services_dir']

    ssh_manager = SSHManager(
        config['ssh']['hostname'],
        config['ssh']['username'],
        config['ssh']['password']
    )

    try:
        ssh_manager.connect()
        with ssh_manager.client.cd(services_dir):
            services = ssh_manager.execute_command('ls').stdout.split()

            for service in services:
                is_ok = service_process(ssh_manager, service)
                if not is_ok:
                    print("Non va bene:", service)
                    services.remove(service)

        """

        docker_manager = DockerManager(ssh_manager)
        services_info = docker_manager.setup_and_zip_services(
            config['ssh']['services_dir']
        )

        for service in services_info:
            ssh_manager.execute_command(
                f'curl -F "chat_id={chat_id}" -F "document=@{service}" '
                f'"https://api.telegram.org/bot{token}/sendDocument"')
        """
    finally:
        pass
        #ssh_manager.disconnect()


if __name__ == "__main__":
    main()
