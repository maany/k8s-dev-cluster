import tempfile
import json

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


class WatchCertManagerEvents(BaseConfiguration):
    def __init__(self, kubeconfig: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig

        self.steps = [
            self.watch_cert_manager_helm_chart,
        ]

    def watch_cert_manager_helm_chart(self, log_prefix: str):
        self.log(log_prefix, colored(
            "Watching Cert Manager Helm Chart", "green"))
        self.watch_namespace_events(
            namespace="cert-manager",
            log_prefix=log_prefix
        )

class WatchChallenges(BaseConfiguration):
    def __init__(self, kubeconfig: str, namespace: str) -> None:
        super().__init__()
        self.kubeconfig = kubeconfig
        self.namespace = namespace

        self.steps = [
            self.watch_challenges
        ]

    def watch_challenges(self, log_prefix: str):
        self.log(log_prefix, colored("Watching Challenges", "green"))
        self.run_process([
            "kubectl", "get", "challenges", "-w"
        ], log_prefix=log_prefix)