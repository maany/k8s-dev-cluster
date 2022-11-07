import os
from pathlib import Path

import click

from api.core.run_context import kube_proxy
from api.cert_manager.cert_manager import InstallCertManagerHelmChart, WatchCertManagerEvents, CreateClusterIssuer, CreateCertificate, WatchChallenges


certmanager_values_default_path = Path(
    __file__).parent.parent / "config" / "certmanager-values.yaml"


@click.group()
@click.option("--kubeconfig",
              default=f"{os.environ.get('HOME', '~')}/.kube/config",
              type=click.Path(exists=True),
              help="Path to kubeconfig file")
@click.pass_context
def cli(context, kubeconfig):
    """
    Install or Configure cert manager on a Kubernetes Cluster
    """
    context.obj = click.Context(cli)
    context.obj.kubeconfig = kubeconfig


@cli.group()
@click.pass_obj
def install(ctx):
    """
    Install Cert Manager
    """
    pass


@install.command()
@click.option("--certmanager-values",
              default=str(certmanager_values_default_path),
              type=click.Path(exists=True),
              help="Path to Cert Manager Helm values file")
@click.pass_obj
def helm_chart(ctx, certmanager_values):
    """
    Install CertManager Helm Chart and Custom Resource Definitions
    """
    InstallCertManagerHelmChart(
        kubeconfig=ctx.kubeconfig,
        certmanager_values=certmanager_values
    ).run()


@install.command()
@click.option("--email", required=True, help="Email address for Cloudflare")
@click.option("--domain", required=True, help="Domain for Let's Encrypt managed by Cloudflare. For example: devmaany.com")
@click.option("--cloudflare-api-token", required=True, help="Cloudflare API Token with Zone:DNS:Edit and Zone:Zone:Read permission")
@click.option("--letsencrypt-environment", type=click.Choice(['staging', 'production']), help="Let's Encrypt Environment. For example: staging or production")
@click.pass_obj
def cluster_issuer(ctx, email, domain, cloudflare_api_token, letsencrypt_environment):
    """
    Install Cluster Issuer and Cloudflare Token as Secret
    """
    with kube_proxy(ctx.kubeconfig) as k:
        CreateClusterIssuer(
            kubeconfig=ctx.kubeconfig,
            email=email,
            domain=domain,
            cloudflare_token=cloudflare_api_token,
            letsencrypt_environment=letsencrypt_environment
        ).run()


@install.command()
@click.option("--email", required=True, help="Email address for Cloudflare")
@click.option("--domain", required=True, help="Domain for Let's Encrypt managed by Cloudflare. For example: devmaany.com")
@click.option("--letsencrypt-environment", type=click.Choice(['staging', 'production']), help="Let's Encrypt Environment. For example: staging or production")
@click.option("--namespace", default="default", help="Namespace where ingress is or will be deployed")
@click.option("--local", is_flag=True, help="Configure certificate for local non-cloud cluster. Set to false for public accessible cluster")
@click.pass_obj
def certificate(ctx, email, domain, letsencrypt_environment, namespace, local):
    """
    Create Certificate for Ingress
    """
    with kube_proxy(ctx.kubeconfig) as k:
        CreateCertificate(
            kubeconfig=ctx.kubeconfig,
            email=email,
            domain=domain,
            letsencrypt_environment=letsencrypt_environment,
            local=local,
            namespace=namespace
        ).run()


@cli.command()
@click.pass_obj
def watch(ctx):
    """
    Watch CertManager Events
    """
    with kube_proxy(ctx.kubeconfig) as k:
        WatchCertManagerEvents(
            kubeconfig=ctx.kubeconfig,
        ).run()

@cli.command()
@click.option("--namespace", "-n", default="default", help="Namespace where ingress is or will be deployed")
@click.pass_obj
def watch_challenges(ctx, namespace):
    """
    Watch Certificates Challenges
    """
    with kube_proxy(ctx.kubeconfig) as k:
        WatchChallenges(
            kubeconfig=ctx.kubeconfig,
            namespace=namespace
        ).run()
