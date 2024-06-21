import yaml
import logging

from ssh_manager import SSHManager

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


def process_service(ssh_manager, service):

    # zip service
    current_path = ssh_manager.execute_command('pwd').stdout.strip()
    zip_name = f'{service}.zip'
    full_path_zip = f"{current_path}/{zip_name}"
    ssh_manager.execute_command(f'rm -rf {full_path_zip}')
    ssh_manager.execute_command(f'zip -r {zip_name} {service}')

    with ssh_manager.client.cd(service):

        output = ssh_manager.execute_command(f"ls").stdout
        if 'docker-compose.yml' not in output:
            return None, None

        # start the service
        ssh_manager.execute_command('docker compose up -d')
        ssh_manager.execute_command('docker ps')

    # get port of service
    try:
        port = get_service_ports_from_docker_ps(ssh_manager, service)
        logging.info(f"Ports for service {service}: {port}")

        return full_path_zip, port
    except:
        pass

    return full_path_zip, None


def main():

    config = load_config()

    telegram_token = config['telegram']['token']
    chat_id = config['telegram']['chat_id']

    hostname = config['ssh']['hostname']
    ssh_manager = SSHManager(
        hostname,
        config['ssh']['username'],
        config['ssh']['password']
    )

    services_dir = config['ssh']['services_dir']

    try:
        ssh_manager.connect()
        with ssh_manager.client.cd(services_dir):
            services = ssh_manager.execute_command('ls -d *').stdout.split()

            for service in services:

                if 'ctf_firewall' in service or '.' in service:
                    continue

                zip_file, port = process_service(ssh_manager, service)
                if not zip_file or not port:
                    logging.info(f"ERROR: {service}")
                    continue

                # send to telegram
                ssh_manager.execute_command(
                    f'curl -F "chat_id={chat_id}" -F "document=@{zip_file}" '
                    f'-F "caption=http://{hostname}:{port}" '
                    f'"https://api.telegram.org/bot{telegram_token}/sendDocument"')

    finally:
        pass


if __name__ == "__main__":
    main()
