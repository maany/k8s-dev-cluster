from termcolor import colored

from api.core.base_configuration import BaseConfiguration


class InstallCertManagerHelmChart(BaseConfiguration):
    def __init__(self, kubeconfig: str, certmanager_values: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.certmanager_values = certmanager_values
        
        self.steps = [
            self.add_cert_manager_helm_repo,
            self.install_cert_manager_helm_chart,
        ]

    def add_cert_manager_helm_repo(self, log_prefix: str):
        self.log(log_prefix, colored("Adding CertManager Helm Repo", "green"))
        self.run_process([
            "helm", "repo", "add", "jetstack",
            "https://charts.jetstack.io"
        ], log_prefix=log_prefix)
        self.run_process([
            "helm", "repo", "update"
        ], log_prefix=log_prefix)
    
    def install_cert_manager_helm_chart(self, log_prefix: str):
        self.log(log_prefix, colored("Installing Cert Manager Helm Chart with CRDs", "green"))
        self.run_process([
            "helm", "install", "cert-manager", "jetstack/cert-manager",
            "--create-namespace", "--namespace", "cert-manager",
            "--values", f"{self.certmanager_values}"
        ], log_prefix=log_prefix)

class WatchCertManagerEvents(BaseConfiguration):
    def __init__(self, kubeconfig: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        
        self.steps = [
            self.watch_cert_manager_helm_chart,
        ]

    def watch_cert_manager_helm_chart(self, log_prefix: str):
        self.log(log_prefix, colored("Watching Cert Manager Helm Chart", "green"))
        self.watch_namespace_events(
            namespace="cert-manager",
            log_prefix=log_prefix
        )