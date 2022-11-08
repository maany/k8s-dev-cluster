import os
import tempfile
import json
import yaml

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
        self.log(log_prefix, colored(
            "Installing Cert Manager Helm Chart with CRDs", "green"))
        self.run_process([
            "helm", "install", "cert-manager", "jetstack/cert-manager",
            "--create-namespace", "--namespace", "cert-manager",
            "--values", f"{self.certmanager_values}"
        ], log_prefix=log_prefix)


class CreateClusterIssuer(BaseConfiguration):
    def __init__(self, kubeconfig: str, email: str, domain: str, cloudflare_token: str, letsencrypt_environment: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.email = email
        self.domain = domain
        self.cloudflare_token = cloudflare_token

        self.secret_cloudflare_token = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "cloudflare-token-secret",
                "namespace": "cert-manager"
            },
            "type": "Opaque",
            "stringData": {
                "cloudflare-token": f"{self.cloudflare_token}"
            }
        }
        if letsencrypt_environment == "staging":
            self.letsencrypt_acme_server = "https://acme-staging-v02.api.letsencrypt.org/directory"
        elif letsencrypt_environment == "production":
            self.letsencrypt_acme_server = "https://acme-v02.api.letsencrypt.org/directory"

        self.cluster_issuer = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "ClusterIssuer",
            "metadata": {
                "name": f"letsencrypt-{letsencrypt_environment}"
            },
            "spec": {
                "acme": {
                    "email": f"{self.email}",
                    "server": f"{self.letsencrypt_acme_server}",
                    "privateKeySecretRef": {
                        "name": f"letsencrypt-{letsencrypt_environment}"
                    },
                    "solvers": [
                        {
                            "dns01": {
                                "cloudflare": {
                                    "email": f"{self.email}",
                                    "apiTokenSecretRef": {
                                        "name": "cloudflare-token-secret",
                                        "key": "cloudflare-token"
                                    }
                                }
                            },
                            'selector': {
                                'dnsZones': [f"{self.domain}"]
                            }
                        }
                    ]
                }
            }
        }

        self.steps = [
            self.create_cloudflare_token_secret,
            self.create_cluster_issuer
        ]

    def create_cloudflare_token_secret(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Creating Cloudflare Token Secret", "green"))
        self.log(log_prefix, json.dumps(
            self.secret_cloudflare_token, indent=4))
        with tempfile.NamedTemporaryFile(mode="w") as f:
            json.dump(self.secret_cloudflare_token, f)
            f.flush()
            self.run_process([
                "kubectl", "apply", "-f", f.name
            ], log_prefix=log_prefix)

    def create_cluster_issuer(self, log_prefix: str):
        self.log(log_prefix, colored("Creating Cluster Issuer", "green"))
        self.log(log_prefix, json.dumps(self.cluster_issuer, indent=4))
        with tempfile.NamedTemporaryFile(mode="w") as f:
            json.dump(self.cluster_issuer, f)
            f.flush()
            self.run_process([
                "kubectl", "apply", "-f", f.name
            ], log_prefix=log_prefix)


class CreateCertificate(BaseConfiguration):
    def __init__(self, kubeconfig: str, email: str, domain: str, letsencrypt_environment: str, local: bool, namespace: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.email = email
        self.domain = domain
        self.namespace = namespace
        self.letsencrypt_environment = letsencrypt_environment
        self.local = local
        if self.local:
            self.certificate_name = f"local-{self.domain.replace('.', '-')}"
            self.secret_name = f"local-{self.domain.replace('.', '-')}-{self.letsencrypt_environment}-tls"
            self.common_name = f"*.local.{self.domain}"
            self.dns_names = [f"*.local.{self.domain}", f"local.{self.domain}"]
        else:
            self.certificate_name = f"{self.domain.replace('.', '-')}"
            self.secret_name = f"{self.domain.replace('.', '-')}-{self.letsencrypt_environment}-tls"
            self.common_name = f"*.{self.domain}"
            self.dns_names = [f"*.{self.domain}", f"{self.domain}"]

        self.certificate = {
            "apiVersion": "cert-manager.io/v1",
            "kind": "Certificate",
            "metadata": {
                "name": self.certificate_name,
                "namespace": self.namespace
            },
            "spec": {
                "secretName": self.secret_name,
                "issuerRef": {
                    "name": f"letsencrypt-{self.letsencrypt_environment}",
                    "kind": "ClusterIssuer"
                },
                "commonName": self.common_name,
                "dnsNames": self.dns_names
            }
        }

        self.steps = [
            self.create_certificate
        ]

    def create_certificate(self, log_prefix: str):
        self.log(log_prefix, colored("Creating Certificate", "green"))
        self.log(log_prefix, json.dumps(self.certificate, indent=4))
        with tempfile.NamedTemporaryFile(mode="w") as f:
            json.dump(self.certificate, f)
            f.flush()
            self.run_process([
                "kubectl", "apply", "-f", f.name
            ], log_prefix=log_prefix)


class BackupCertManager(BaseConfiguration):
    def __init__(self, kubeconfig: str, backup_dir: str, letsencrypt_environment: str, certificate_namespace: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.backup_dir = backup_dir
        self.letsencrypt_environment = letsencrypt_environment
        self.tls_secret_name = f"letsencrypt-{letsencrypt_environment}"
        self.certificate_namespace = certificate_namespace
        self.steps = [
            self.backup_x509_certificates,
            self.backup_cloudflare_token_secret,
            self.backup_cluster_issuer,
            self.backup_certificates
        ]

    def backup_x509_certificates(self, log_prefix: str):
        self.log(log_prefix, colored(f"Backing up x509 certificate {self.tls_secret_name}", "green"))
        rcode, out, err = self.run_process([
            "kubectl", "-n", "cert-manager",
            "get", "secret", self.tls_secret_name,
            "-o", "yaml"
        ], log_prefix=log_prefix)
        if rcode != 0:
            self.log(log_prefix, colored(f"Failed to get secret {self.tls_secret_name}", "red"))
            self.log(log_prefix, colored(err, "red"))
            return
        secret = yaml.safe_load(out)
        secret["metadata"].pop("resourceVersion")
        secret["metadata"].pop("uid")
        backup_path = os.path.join(self.backup_dir, "x509_secret.yaml")
        self.log(log_prefix, colored(f"Backing up x509 certificate {self.tls_secret_name} at {backup_path}", "green"))
        with open(backup_path, "w") as f:
            yaml.dump(secret, f)

    def backup_cloudflare_token_secret(self, log_prefix: str):
        self.log(log_prefix, colored(f"Backing up Cloudflare Token Secret", "green"))
        rcode, out, err = self.run_process([
            "kubectl", "-n", "cert-manager",
            "get", "secret", "cloudflare-token-secret",
            "-o", "yaml"
        ], log_prefix=log_prefix)
        if rcode != 0:
            self.log(log_prefix, colored(f"Failed to get secret cloudflare-token-secret", "red"))
            self.log(log_prefix, colored(err, "red"))
            return
        secret = yaml.safe_load(out)
        secret["metadata"].pop("resourceVersion")
        secret["metadata"].pop("uid")
        backup_path = os.path.join(self.backup_dir, "cloudflare_token_secret.yaml")
        self.log(log_prefix, colored(f"Backing up Cloudflare Token Secret at {backup_path}", "green"))
        with open(backup_path, "w") as f:
            yaml.dump(secret, f)

    
    def backup_cluster_issuer(self, log_prefix: str):
        self.log(log_prefix, colored(f"Backing up ClusterIssuer", "green"))
        rcode, out, err = self.run_process([
            "kubectl", "-n", "cert-manager",
            "get", "clusterissuer", f"letsencrypt-{self.letsencrypt_environment}",
            "-o", "yaml"
        ], log_prefix=log_prefix)
        if rcode != 0:
            self.log(log_prefix, colored(f"Failed to get clusterissuer letsencrypt-{self.letsencrypt_environment}", "red"))
            self.log(log_prefix, colored(err, "red"))
            return
        cluster_issuer = yaml.safe_load(out)
        cluster_issuer["metadata"].pop("resourceVersion")
        cluster_issuer["metadata"].pop("uid")
        backup_path = os.path.join(self.backup_dir, "cluster_issuer.yaml")
        self.log(log_prefix, colored(f"Backing up ClusterIssuer at {backup_path}", "green"))
        with open(backup_path, "w") as f:
            yaml.dump(cluster_issuer, f)

    def backup_certificates(self, log_prefix: str):
        self.log(log_prefix, colored(f"Backing up Certificates", "green"))
        rcode, out, err = self.run_process([
            "kubectl", "-n", self.certificate_namespace,
            "get", "certificates",
            "-o", "yaml"
        ], log_prefix=log_prefix)
        if rcode != 0:
            self.log(log_prefix, colored(f"Failed to get certificates", "red"))
            self.log(log_prefix, colored(err, "red"))
            return
        certificates = yaml.safe_load(out)
        for certificate in certificates["items"]:
            certificate["metadata"].pop("resourceVersion")
            certificate["metadata"].pop("uid")
        backup_path = os.path.join(self.backup_dir, "certificates.yaml")
        self.log(log_prefix, colored(f"Backing up Certificates at {backup_path}", "green"))
        with open(backup_path, "w") as f:
            yaml.dump(certificates, f)


class RestoreCertManager(BaseConfiguration):
    def __init__(self, kubeconfig: str, backup_dir: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.backup_dir = backup_dir
        self.steps = [
            self.restore_x509_certificates,
            self.wait_10s,
            self.restore_cloudflare_token_secret,
            self.wait_10s,
            self.restore_certificates,
            self.wait_10s,
            self.restore_cluster_issuer,
        ]

    def restore_x509_certificates(self, log_prefix: str):
        backup_path = os.path.join(self.backup_dir, "x509_secret.yaml")
        self.log(log_prefix, colored(f"Restoring x509 certificate from {backup_path}", "green"))
        with open(backup_path, "r") as f:
            secret = yaml.safe_load(f)
        with tempfile.NamedTemporaryFile(mode="w") as f:
            yaml.dump(secret, f)
            f.flush()
            self.run_process([
                "kubectl", "-n", "cert-manager",
                "apply", "-f", f.name
            ], log_prefix=log_prefix)

    def restore_cloudflare_token_secret(self, log_prefix: str):
        backup_path = os.path.join(self.backup_dir, "cloudflare_token_secret.yaml")
        self.log(log_prefix, colored(f"Restoring Cloudflare Token Secret from {backup_path}", "green"))
        with open(backup_path, "r") as f:
            secret = yaml.safe_load(f)
        with tempfile.NamedTemporaryFile(mode="w") as f:
            yaml.dump(secret, f)
            f.flush()
            self.run_process([
                "kubectl", "-n", "cert-manager",
                "apply", "-f", f.name
            ], log_prefix=log_prefix)

    def restore_cluster_issuer(self, log_prefix: str):
        backup_path = os.path.join(self.backup_dir, "cluster_issuer.yaml")
        self.log(log_prefix, colored(f"Restoring ClusterIssuer from {backup_path}", "green"))
        with open(backup_path, "r") as f:
            cluster_issuer = yaml.safe_load(f)
        with tempfile.NamedTemporaryFile(mode="w") as f:
            yaml.dump(cluster_issuer, f)
            f.flush()
            self.run_process([
                "kubectl", "-n", "cert-manager",
                "apply", "-f", f.name
            ], log_prefix=log_prefix)

    def restore_certificates(self, log_prefix: str):
        backup_path = os.path.join(self.backup_dir, "certificates.yaml")
        self.log(log_prefix, colored(f"Restoring Certificates from {backup_path}", "green"))
        with open(backup_path, "r") as f:
            certificates = yaml.safe_load(f)
        with tempfile.NamedTemporaryFile(mode="w") as f:
            yaml.dump(certificates, f)
            f.flush()
            self.run_process([
                "kubectl",
                "apply", "-f", f.name
            ], log_prefix=log_prefix)
