import logging
from api.core.base_configuration import BaseConfiguration
from termcolor import colored

class InstallLonghorn(BaseConfiguration):
    def __init__(self, kubeconfig: str, longhorn_values: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.longhorn_values = longhorn_values
        self.steps = [
            self.add_longhorn_helm_repo,
            self.update_helm_repo,
            self.install_longhorn_helm_chart,
        ]

    def add_longhorn_helm_repo(self, log_prefix: str):
        self.log(log_prefix, "Adding Longhorn Helm repo", logging.INFO)
        self.run_process(["helm", "repo", "add", "longhorn", "https://charts.longhorn.io"],
                         log_prefix=log_prefix)
    
    def update_helm_repo(self, log_prefix: str):
        self.log(log_prefix, colored("Updating Helm repo", "blue"), logging.INFO)
        self.run_process(["helm", "repo", "update"], log_prefix=log_prefix)

    def install_longhorn_helm_chart(self, log_prefix: str):
        self.log(log_prefix, colored("Installing Longhorn Helm chart", "blue"), logging.INFO)
        self.run_process([
            "helm", "install", "longhorn", "longhorn/longhorn", 
            "-f", self.longhorn_values, 
            "--create-namespace",
            "-n", "longhorn-system"
            ],
            log_prefix=log_prefix
        )

class WatchLonghornEvents(BaseConfiguration):
    def __init__(self, kubeconfig: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.steps = [
            self.watch_longhorn_events,
        ]

    def watch_longhorn_events(self, log_prefix: str):
        self.log(log_prefix, colored("Watching Longhorn events", "blue"), logging.INFO)
        self.watch_namespace_events(
            namespace="longhorn-system",
            log_prefix=log_prefix
        )

class ExposeLonghornUIMetalLB(BaseConfiguration):
    def __init__(self, kubeconfig: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.steps = [
            self.expose_longhorn_ui_metallb,
            self.wait_10s,
            self.get_loadbalancer_ip,
        ]

    def expose_longhorn_ui_metallb(self, log_prefix: str):
        self.log(log_prefix, colored("Exposing Longhorn UI with MetalLB", "blue"), logging.INFO)
        self.run_process([
            "kubectl", "-n", "longhorn-system", "patch", "svc", "longhorn-frontend",
            "-p", '{"spec": {"type": "LoadBalancer"}}'
        ], log_prefix=log_prefix)
    
    def get_loadbalancer_ip(self, log_prefix: str):
        self.log(log_prefix, colored("Getting LoadBalancer IP", "blue"), logging.INFO)
        rcode, out, err = self.run_process([
            "kubectl", "-n", "longhorn-system", "get", "svc", "longhorn-frontend",
            "-o", "jsonpath='{.status.loadBalancer.ingress[0].ip}'"
        ], log_prefix=log_prefix)
        self.log(log_prefix, colored(f"LoadBalancer IP: {out}", "green", "on_yellow"), logging.INFO)

class ExposeLonghornUI(BaseConfiguration):
    def __init__(self, kubeconfig: str, port: int):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.port = port
        self.steps = [
            self.expose_longhorn_ui,
        ]

    def expose_longhorn_ui(self, log_prefix: str):
        self.log(log_prefix, colored("Exposing Longhorn UI", "blue"), logging.INFO)
        self.run_process([
            "kubectl", "port-forward", "svc/longhorn-frontend", f"{self.port}:80", 
            "-n", "longhorn-system"
            ],
            log_prefix=log_prefix
        )
