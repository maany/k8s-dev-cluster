import logging
import time
from termcolor import colored

from api.core.base_configuration import BaseConfiguration


class InstallMetalLb(BaseConfiguration):
    def __init__(self, kubeconfig: str, metallb_values: str, pool_name: str, start_ip: str, end_ip: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.metallb_values = metallb_values
        self.pool_name = pool_name
        self.start_ip = start_ip
        self.end_ip = end_ip

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

        self.steps = [
            self.add_metallb_helm_repo,
            self.update_helm_repo,
            self.install_metallb_helm_chart,
            self.add_namespace_labels,
            self.create_metallb_custom_resources
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

    def create_metallb_custom_resources(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Creating MetalLB custom resources", "blue"), logging.INFO)

        self.log(log_prefix, colored(f"Creating MetalLB AddressPool", "yellow"), logging.INFO)
        self.log(log_prefix, colored(f"AddressPool: {self.ip_address_pool}", "yellow"), logging.INFO)
        
        self.create_from_dict(
            resource_dict=self.ip_address_pool,
            namespace="metallb-system",
            log_prefix=log_prefix
        )

        self.log(log_prefix, colored(f"Creating MetalLB L2Advertisement", "yellow"), logging.INFO)
        self.log(log_prefix, colored(f"L2Advertisement: {self.l2_advertisement}", "yellow"), logging.INFO)

        self.create_from_dict(
            resource_dict=self.l2_advertisement,
            namespace="metallb-system",
            log_prefix=log_prefix
        )


class UninstallMetalLb(BaseConfiguration):
    def __init__(self, kubeconfig: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.steps = [
            self.uninstall_metallb_helm_chart,
            self.delete_metallb_namespace
        ]

    def uninstall_metallb_helm_chart(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Uninstalling MetalLB Helm chart", "blue"), logging.INFO)
        self.run_process([
            "helm", "uninstall", "metallb",
            "-n", "metallb-system"
        ],
            log_prefix=log_prefix
        )

    def delete_metallb_namespace(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Deleting all L2Advertisements, AddressPool from MetalLB namespace", "blue"), logging.INFO)
        self.run_process([
            "kubectl", "delete", "AddressPool", "L2Advertisement", "all", "-n" ,"metallb-system"
        ],
            log_prefix=log_prefix
        )
        
        self.log(log_prefix, colored(
            "Deleting MetalLB namespace", "blue"), logging.INFO)
        self.run_process([
            "kubectl", "delete", "namespace", "metallb-system"
        ],
            log_prefix=log_prefix
        )
        
