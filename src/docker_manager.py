import logging


class DockerManager:
    def __init__(self, ssh_manager):
        self.ssh_manager = ssh_manager

    def discover_services(self, base_dir):
        output, errors = self.ssh_manager.execute_command(f"cd {base_dir} && ls -d */")
        if errors:
            logging.error(f"Error discovering services: {errors}")
            raise RuntimeError(f"Error discovering services: {errors}")
        return [dir.rstrip('/') for dir in output.strip().split()]

    def setup_and_zip_services(self, base_dir):
        services_info = []

        for service_dir in self.discover_services(base_dir):
            if 'backup' in service_dir or 'services' in service_dir:
                continue

            logging.info(f"Setting up and zipping {base_dir}{service_dir}")
            self.ssh_manager.execute_command(f"cd {base_dir}{service_dir} && docker compose up -d")

            zip_path = f"{service_dir.strip('/')}.zip"
            _, error = self.ssh_manager.execute_command(f"zip -r {zip_path} {base_dir}{service_dir}")
            if error:
                logging.error(f"Failed to zip {base_dir}{service_dir}: {error}")
                continue

            services_info.append(zip_path)

        return services_info
