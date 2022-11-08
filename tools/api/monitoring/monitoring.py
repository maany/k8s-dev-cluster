import yaml
import json
from tempfile import NamedTemporaryFile

from termcolor import colored

from api.core.base_configuration import BaseConfiguration


class InstallKubePrometheusStack(BaseConfiguration):
    def __init__(self, kubeconfig: str, values: str, control_plane_nodes: list, grafana_user: str, grafana_password: str):
        super().__init__()
        self.kubeconfig = kubeconfig
        self.values = values
        self.control_plane_nodes = [str(node).replace("'", "") for node in control_plane_nodes]
        self.grafana_user = grafana_user
        self.grafana_password = grafana_password
        self.steps = [
            self.create_namespace,
            self.create_grafana_secret,
            self.install_helm_repo
        ]

    def update_endpoints(self):
        with open(self.values, "r") as f:
            values = yaml.safe_load(f)
        values['kubeControllerManager']['endpoints'] = self.control_plane_nodes
        values['kubeScheduler']['endpoints'] = self.control_plane_nodes
        values['kubeEtcd']['endpoints'] = self.control_plane_nodes
        values['kubeProxy']['endpoints'] = self.control_plane_nodes
        return values

    def create_namespace(self, log_prefix: str):
        self.log(log_prefix, colored("Creating Monitoring Namespace", "green"))
        #check if namespace exists
        existing_namespaces = self.v1.list_namespace()
        if "monitoring" in [namespace.metadata.name for namespace in existing_namespaces.items]:
            self.log(log_prefix, colored("Monitoring Namespace already exists", "yellow"))
            return
        self.run_process([
            "kubectl", "create", "namespace", "monitoring"
        ], log_prefix=log_prefix)

    def create_grafana_secret(self, log_prefix: str):
        secrets = self.v1.list_namespaced_secret(namespace="monitoring")
        if "grafana-admin-credentials" in [secret.metadata.name for secret in secrets.items]:
            self.log(log_prefix, colored("Grafana Secret already exists", "yellow"))
            self.log(log_prefix, colored("Deleting existing secret grafana-admin-credentials", "red"))
            self.v1.delete_namespaced_secret(
                name="grafana-admin-credentials",
                namespace="monitoring"
            )

        self.log(log_prefix, colored("Creating Grafana Secret", "green"))
        self.run_process([
            "kubectl", "create", "secret", "generic", "grafana-admin-credentials", 
            "--from-literal=admin-user={}".format(self.grafana_user),
            "--from-literal=admin-password={}".format(self.grafana_password), 
            "--namespace", "monitoring"
        ], log_prefix=log_prefix)

    def install_helm_repo(self, log_prefix: str):
        self.log(log_prefix, colored("Installing Kube Prometheus Stack Helm Repo", "green"))
        self.run_process([
            "helm", "repo", "add", "prometheus-community", "https://prometheus-community.github.io/helm-charts"
        ], log_prefix=log_prefix)

        self.run_process([
            "helm", "repo", "update"
        ], log_prefix=log_prefix)

        updated_values = self.update_endpoints()
        self.log(log_prefix, colored("Updated Kube Prometheus Stack Helm Values ( Master Node IPs)", "green"))
        with NamedTemporaryFile(mode="w") as values:
            json_data = json.dumps(updated_values, indent=4)
            values.write(json_data)
            self.log(log_prefix, colored(f"Values {json_data}", "green"))
            self.run_process([
                "helm", "install", "monitoring", 
                "prometheus-community/kube-prometheus-stack",
                "-f", values.name,
                "--namespace", "monitoring"
            ], log_prefix=log_prefix)


class UninstallKubePrometheusStack(BaseConfiguration):
    def __init__(self, kubeconfig: str):
        super().__init__()
        self.kubeconfig = kubeconfig

        self.steps = [
            self.uninstall_helm_repo,
            self.delete_namespace
        ]

    def uninstall_helm_repo(self, log_prefix: str):
        self.log(log_prefix, colored("Uninstalling Kube Prometheus Stack Helm Repo", "green"))
        self.run_process([
            "helm", "uninstall", "monitoring", "--namespace", "monitoring"
        ], log_prefix=log_prefix)

    def delete_namespace(self, log_prefix: str):
        self.log(log_prefix, colored("Deleting Monitoring Namespace", "green"))
        self.run_process([
            "kubectl", "delete", "namespace", "monitoring"
        ], log_prefix=log_prefix)