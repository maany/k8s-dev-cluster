import logging
from pathlib import Path
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