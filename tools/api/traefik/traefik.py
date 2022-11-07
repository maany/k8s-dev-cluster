import logging
import base64
import tempfile
import json

from passlib.hash import apr_md5_crypt
from termcolor import colored

from api.core.base_configuration import BaseConfiguration


class InstallTraefikHelmChart(BaseConfiguration):
    def __init__(self, kubeconfig: str, traefik_values) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.traefik_values = traefik_values

        self.steps = [
            self.add_traefik_helm_repo,
            self.update_helm_repo,
            self.install_traefik_helm_chart,
        ]

    def create_traefik_namespace(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Creating Traefik namespace", "blue"), logging.INFO)
        self.run_process(["kubectl", "create", "namespace", "traefik"],
                         log_prefix=log_prefix)

    def add_traefik_helm_repo(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Adding Traefik Helm repo", "blue"), logging.INFO)
        self.run_process(["helm", "repo", "add", "traefik", "https://helm.traefik.io/traefik"],
                         log_prefix=log_prefix)

    def update_helm_repo(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Updating Helm repo", "blue"), logging.INFO)
        self.run_process(["helm", "repo", "update"], log_prefix=log_prefix)

    def install_traefik_helm_chart(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Installing Traefik Helm chart", "blue"), logging.INFO)
        self.run_process([
            "helm", "install", "traefik", "traefik/traefik",
            "-f", self.traefik_values,
            "--create-namespace",
            "-n", "traefik"
        ],
            log_prefix=log_prefix
        )

class InstallTraefikDefaultHeaders(BaseConfiguration):
    def __init__(self, kubeconfig: str, traefik_default_headers: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.traefik_default_headers = traefik_default_headers

        self.steps = [
            self.install_traefik_default_headers,
        ]

    def install_traefik_default_headers(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Installing Traefik default headers", "blue"), logging.INFO)
        self.run_process([
            "kubectl", "apply", "-f", self.traefik_default_headers,
        ],
            log_prefix=log_prefix
        )

class InstallTraefikDashboard(BaseConfiguration):
    def __init__(self, kubeconfig: str, dashboard_username: str, dashboard_password: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.dashboard_username = dashboard_username
        self.dashboard_password = dashboard_password
        self.hashed_passwd = self.hash_password(self.dashboard_password)
        self.dashboard_user = f"{self.dashboard_username}:{self.hashed_passwd}"
        self.dashboard_user_b64 = base64.b64encode(
            self.dashboard_user.encode('utf-8')
        ).decode("utf-8")
        
        self.dashboard_secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "traefik-dashboard-auth",
                "namespace": "traefik"
            },
            "type": "Opaque",
            "data": {
                "users": self.dashboard_user_b64
            }


        }
        self.steps = [
            self.install_traefik_dashboard_secret,
        ]

    def hash_password(self, password: str):
        return apr_md5_crypt.hash(password)

    def install_traefik_dashboard_secret(self, log_prefix: str):
        self.log(log_prefix, colored(f"htpasswd entry with apr1 hash of password: {self.dashboard_user}", "blue"), logging.INFO)
        self.log(log_prefix, f"Secret: {json.dumps(self.dashboard_secret, indent=4)}", logging.INFO)
        self.log(log_prefix, colored(
            "Installing Traefik dashboard secret", "blue"), logging.INFO)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write(json.dumps(self.dashboard_secret, indent=4))
            tmp.close()
            self.run_process([
                "kubectl", "apply", "-f", tmp.name,
            ],
                log_prefix=log_prefix
            )


class WatchTraefikEvents(BaseConfiguration):
    def __init__(self, kubeconfig: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.steps = [
            self.watch_traefik_events,
        ]

    def watch_traefik_events(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Watching Traefik events", "blue"), logging.INFO)
        self.watch_namespace_events(
            namespace="traefik",
            log_prefix=log_prefix
        )

class GetTraefikLoadBalancerIP(BaseConfiguration):
    def __init__(self, kubeconfig: str, ) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig

        self.steps = [
            self.get_traefik_loadbalancer_ip,
        ]

    def get_traefik_loadbalancer_ip(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Getting Traefik LoadBalancer IP", "blue"), logging.INFO)
        rcode, out, err = self.run_process([
            "kubectl", "get", "service", "traefik", "-n", "traefik",
            "-o", "jsonpath='{.status.loadBalancer.ingress[0].ip}'"
        ],
            log_prefix=log_prefix
        )
        self.log("Traefik LoadBalancer IP", colored(out, "green", "on_yellow"), logging.INFO)


class UninstallTraefikHelmChart(BaseConfiguration):
    def __init__(self, kubeconfig: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig

        self.steps = [
            self.uninstall_traefik_helm_chart,
        ]

    def uninstall_traefik_helm_chart(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Uninstalling Traefik Helm chart", "blue"), logging.INFO)
        self.run_process([
            "helm", "uninstall", "traefik", "-n", "traefik"
        ],
            log_prefix=log_prefix
        )

class UninstallTraefikDefaultHeaders(BaseConfiguration):
    def __init__(self, kubeconfig: str, traefik_default_headers: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.traefik_default_headers = traefik_default_headers

        self.steps = [
            self.uninstall_traefik_default_headers,
        ]

    def uninstall_traefik_default_headers(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Uninstalling Traefik default headers", "blue"), logging.INFO)
        self.run_process([
            "kubectl", "delete", "-f", self.traefik_default_headers,
        ],
            log_prefix=log_prefix
        )
