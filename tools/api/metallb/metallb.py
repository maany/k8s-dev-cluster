import logging
import time
import json
from termcolor import colored

from kubernetes.client.exceptions import ApiException

from api.core.base_configuration import BaseConfiguration


class InstallMetalLbHelmChart(BaseConfiguration):
    def __init__(self, kubeconfig: str, metallb_values: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.metallb_values = metallb_values
       
        self.steps = [
            self.add_metallb_helm_repo,
            self.update_helm_repo,
            self.install_metallb_helm_chart,
            self.add_namespace_labels,
        ]

    def add_metallb_helm_repo(self, log_prefix: str):
        self.log(log_prefix, "Adding MetalLB Helm repo", logging.INFO)
        self.run_process(["helm", "repo", "add", "metallb", "https://metallb.github.io/metallb"],
                         log_prefix=log_prefix)

    def update_helm_repo(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Updating Helm repo", "blue"), logging.INFO)
        self.run_process(["helm", "repo", "update"], log_prefix=log_prefix)

    def install_metallb_helm_chart(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Installing MetalLB Helm chart", "blue"), logging.INFO)
        self.run_process([
            "helm", "install", "metallb", "metallb/metallb",
            "-f", self.metallb_values,
            "--create-namespace",
            "-n", "metallb-system"
        ],
            log_prefix=log_prefix
        )

        self.log(log_prefix, colored("Sleeping for 15 seconds", "blue"), logging.INFO)
        time.sleep(15)

    def add_namespace_labels(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Adding MetalLB namespace labels", "blue"), logging.INFO)
        self.run_process([
            "kubectl", "label", "namespace", "metallb-system",
            "pod-security.kubernetes.io/enforce=privileged",
            "pod-security.kubernetes.io/audit=privileged",
            "pod-security.kubernetes.io/warn=privileged",
        ],
            log_prefix=log_prefix
        )


class InstallCustomResources(BaseConfiguration):
     
    def __init__(self, kubeconfig: str, pool_name: str, start_ip: str, end_ip: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.pool_name = pool_name
        self.start_ip = start_ip
        self.end_ip = end_ip

        self.steps = [
            self.create_metallb_custom_resources
        ]

        self.ip_address_pool = {
            "apiVersion": "metallb.io/v1beta1",
            "kind": "AddressPool",
            "metadata": {
                "name": f"{self.pool_name}-pool",
                "namespace": "metallb-system"
            },
            "spec": {
                "addresses": [
                    f"{self.start_ip}-{self.end_ip}"
                ]
            }
        }

        self.l2_advertisement = {
            "apiVersion": "metallb.io/v1beta1",
            "kind": "L2Advertisement",
            "metadata": {
                "name": f"{self.pool_name}-advertisement",
                "namespace": "metallb-system"
            },
            "spec": {
                "ipAddressPools": [
                    f"{self.pool_name}-pool"
                ]
            }
        }

    def create_metallb_custom_resources(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Creating MetalLB custom resources", "blue"), logging.INFO)

        self.log(log_prefix, colored(f"Creating MetalLB AddressPool", "yellow"), logging.INFO)
        self.log(log_prefix, colored(f"AddressPool: {self.ip_address_pool}", "yellow"), logging.INFO)
        
        self.run_process([ "echo", '"', f"{json.dumps(self.ip_address_pool)}", '"', " | ", "kubectl", "apply", "-f", "-"],
                            log_prefix=log_prefix)

        self.log(log_prefix, colored(f"Creating MetalLB L2Advertisement", "yellow"), logging.INFO)
        self.log(log_prefix, colored(f"L2Advertisement: {self.l2_advertisement}", "yellow"), logging.INFO)

        self.run_process(["echo", '"', f"{json.dumps(self.l2_advertisement)}", '"', " | ", "kubectl", "apply", "-f", "-"],
                            log_prefix=log_prefix)


class UninstallMetalLb(BaseConfiguration):
    def __init__(self, kubeconfig: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.steps = [
            self.uninstall_metallb_helm_chart,
            self.delete_metallb_namespace
        ]

    def helm_chart_is_installed(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Checking if MetalLB Helm chart is installed", "blue"), logging.INFO)
        code, out, err = self.run_process([
            "helm", "list", "-n", "metallb-system"
        ],
            log_prefix=log_prefix
        )
        if "metallb-system" in out:
            return True
        return False
        
    def uninstall_metallb_helm_chart(self, log_prefix: str):
        if self.helm_chart_is_installed(log_prefix):
            self.log(log_prefix, colored(
                "Uninstalling MetalLB Helm chart", "blue"), logging.INFO)
            self.run_process([
                "helm", "uninstall", "metallb",
                "-n", "metallb-system"
            ],
                log_prefix=log_prefix
            )
        else:
            self.log(log_prefix, colored(
                "MetalLB Helm chart is not installed", "blue"), logging.INFO)

    def delete_metallb_namespace(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Deleting MetalLB namespace", "blue"), logging.INFO)
        try:
            self.v1.delete_namespace(name="metallb-system")
        except ApiException as e:
            if e.status == 404:
                self.log(log_prefix, colored(
                    "MetalLB namespace does not exist", "blue"), logging.INFO)
            else:
                self.log(log_prefix, colored(
                    f"Error deleting MetalLB namespace: {e}", "red"), logging.ERROR)
                raise e

        
class WatchMetalLbEvents(BaseConfiguration):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.steps = [self.watch_namespace_events]

    def watch_namespace_events(self, log_prefix: str):
        super().watch_namespace_events("metallb-system", log_prefix)