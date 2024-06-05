class DockerManager:
    def __init__(self, ssh_manager):
        self.ssh_manager = ssh_manager

    def discover_services(self):
        output, errors = self.ssh_manager.execute_command("ls -d */")
        if errors:
            print(f"Error discovering services: {errors}")
            return []

        service_dirs = output.strip().split()
        return [dir.rstrip('/') for dir in service_dirs]

    def setup_and_zip_services(self):
        service_dirs = self.discover_services()

        services_info = []
        for service_dir in service_dirs:
            if 'backup' in service_dir:
                continue
            if 'services' in service_dir:
                continue

            print(f"[+] Setting up and zipping {service_dir}")

            self.ssh_manager.execute_command(f"cd {service_dir} && docker compose up -d")

            zip_path = f"{service_dir.strip('/')}.zip"
            self.ssh_manager.execute_command(f"zip -r {zip_path} {service_dir}")
            services_info.append(zip_path)

        return services_info
