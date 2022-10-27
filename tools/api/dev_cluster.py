from termcolor import colored
from api.core.base_configuration import BaseConfiguration
import time
import os

class DevClusterConfiguration(BaseConfiguration):
    def __init__(self, kubeconfig) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig

        self.steps = [
            self.check_config,
            self.restart_coredns_pods,
            self.restart_metrics_server,
        ]

    def check_config(self, log_prefix: str | None = None, **kwargs):
        if self.kubeconfig is None:
            self.log(self.__class__.__name__, colored(
                "No kubeconfig provided", "red", attrs=["bold", "blink"]))
            raise ValueError(
                "No kubeconfig provided. Please provide a kubeconfig using the --kube-config flag")
        self.env = {"KUBECONFIG": self.kubeconfig, "PATH": os.environ["PATH"]}


    def restart_coredns_pods(self, log_prefix: str | None = None, **kwargs):
        self.log(log_prefix, colored("Restarting coredns pods", "green"))
        self.run_process([
            "kubectl", "rollout", "restart", "deployment/coredns", "-n", "kube-system"
        ], log_prefix=log_prefix)
        self.log(log_prefix, colored("Sleeping for 10s", "yellow"))
        time.sleep(10)

    def restart_metrics_server(self, log_prefix: str | None = None, **kwargs):
        self.log(log_prefix, colored("Restarting metrics server", "green"))
        self.run_process([
            "kubectl", "rollout", "restart", "deployment/metrics-server", "-n", "kube-system"
        ], log_prefix=log_prefix)
        self.log(log_prefix, colored("Sleeping for 20s", "yellow"))
        time.sleep(20)
