from api.core.base_configuration import BaseConfiguration
import logging

class LonghornConfiguration(BaseConfiguration):
    def __init__(self, kubeconfig: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.steps = [
            self.add_longhorn_helm_repo
        ]

    def add_longhorn_helm_repo(self, log_prefix: str):
        self.log(log_prefix, "Adding Longhorn Helm repo", logging.INFO)
        self.run_process(["helm", "repo", "add", "longhorn", "https://charts.longhorn.io"],
                         log_prefix=log_prefix)