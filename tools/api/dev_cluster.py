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


class InstallCilium(BaseConfiguration):
    def __init__(self, kubeconfig, kubemaster_ip) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.kubemaster_ip = kubemaster_ip

        self.steps = [
            self.check_config,
            self.add_helm_repo,
            self.install_cilium,
            self.wait_for_cilium_status,
            self.restart_hubble,
            self.wait_for_cilium_status
        ]

    def check_config(self, log_prefix: str | None = None, **kwargs):
        if self.kubeconfig is None:
            self.log(self.__class__.__name__, colored(
                "No kubeconfig provided", "red", attrs=["bold", "blink"]))
            raise ValueError(
                "No kubeconfig provided. Please provide a kubeconfig using the --kube-config flag")
        self.env = {"KUBECONFIG": self.kubeconfig, "PATH": os.environ["PATH"]}

        if self.kubemaster_ip is None:
            self.log(self.__class__.__name__, colored(
                "No kubemaster ip provided", "red", attrs=["bold", "blink"]))
            raise ValueError(
                "No kubemaster ip provided. Please provide a kubemaster ip using the --kubemaster-ip flag")
    
    def wait_for_cilium(self, log_prefix: str | None = None, **kwargs):
        self.log(log_prefix, colored("Waiting for cilium", "green"))
        self.run_process([
            "kubectl", "wait", "--for=condition=ready", "pod", "-l", "k8s-app=cilium", "-n", "kube-system", "--timeout=6000s"
        ], log_prefix=log_prefix)

    def wait_for_cilium_status(self, log_prefix: str | None = None, **kwargs):
        self.log(log_prefix, colored("Waiting for cilium status", "green"))
        self.run_process([
            "cilium", "status", "--wait"
        ], log_prefix=log_prefix)

    def add_helm_repo(self, log_prefix: str | None = None, **kwargs):
        self.log(log_prefix, colored("Installing cilium helm repo", "green"))
        self.run_process([
            "helm", "repo", "add", "cilium", "https://helm.cilium.io/"
        ], log_prefix=log_prefix)
        
    def install_cilium(self, log_prefix: str | None = None, **kwargs):
        self.log(log_prefix, colored("Installing cilium", "green"))
        self.run_process([
            "helm", "install", "cilium", "cilium/cilium",
            "--version", "1.12.3",
            "--namespace", "kube-system",
            "--set", f"global.k8sServiceHost={self.kubemaster_ip}",
            "--set", f"global.k8sServicePort=6443",
            "--set", "hubble.ui.enabled=true",
            "--set", "hubble.relay.enabled=true",
        ], log_prefix=log_prefix)

    def restart_hubble(self, log_prefix: str | None = None, **kwargs):
        self.log(log_prefix, colored("Restarting hubble", "green"))
        self.run_process([
            "kubectl", "rollout", "restart", "deployment/hubble-relay", "-n", "kube-system"
        ], log_prefix=log_prefix)
        self.log(log_prefix, colored("Sleeping for 10s", "yellow"))
        time.sleep(10)
        self.log(log_prefix, colored("Restarting hubble-ui", "green"))
        self.run_process([
            "kubectl", "rollout", "restart", "deployment/hubble-ui", "-n", "kube-system"
        ], log_prefix=log_prefix)


class ExposeHubble(BaseConfiguration):
    def __init__(self, kubeconfig) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig

        self.steps = [
            self.check_config,
            self.expose_hubble_ui,
            self.wait_10s,
            self.get_loadbalancer_ip
        ]

    def check_config(self, log_prefix: str | None = None, **kwargs):
        if self.kubeconfig is None:
            self.log(self.__class__.__name__, colored(
                "No kubeconfig provided", "red", attrs=["bold", "blink"]))
            raise ValueError(
                "No kubeconfig provided. Please provide a kubeconfig using the --kube-config flag")
        self.env = {"KUBECONFIG": self.kubeconfig, "PATH": os.environ["PATH"]}

    def expose_hubble_ui(self, log_prefix: str | None = None, **kwargs):
        self.log(log_prefix, colored("Exposing hubble ui", "green"))
        self.run_process([
            "kubectl", "-n", "kube-system", "patch", "svc", "hubble-ui",
            "-p", '{"spec": {"type": "LoadBalancer"}}'
        ], log_prefix=log_prefix)

    def get_loadbalancer_ip(self, log_prefix: str | None = None, **kwargs):
        self.log(log_prefix, colored("Getting loadbalancer ip", "green"))
        rcode, out, err = self.run_process([
            "kubectl", "-n", "kube-system", "get", "svc", "hubble-ui", "-o", "jsonpath='{.status.loadBalancer.ingress[0].ip}'"
        ], log_prefix=log_prefix)
        self.log(log_prefix, colored(f"Loadbalancer ip: {out}", "green", "on_yellow"))
