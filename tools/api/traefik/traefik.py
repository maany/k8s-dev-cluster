import logging


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