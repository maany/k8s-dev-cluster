import logging

from api.core.base_configuration import BaseConfiguration
from termcolor import colored

class InstallLonghorn(BaseConfiguration):
    def __init__(self, kubeconfig: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.steps = [
            self.add_longhorn_helm_repo
        ]

    def add_longhorn_helm_repo(self, log_prefix: str):
        self.log(log_prefix, colored("Adding Longhorn Helm repo", "blue"), logging.INFO)
        self.run_process(["helm", "repo", "add", "longhorn", "https://charts.longhorn.io"],
                         log_prefix=log_prefix)
    
    