import os
from pathlib import Path

import click

from api.core.run_context import kube_proxy
from api.cert_manager.cert_manager import InstallCertManagerHelmChart, WatchCertManagerEvents


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
    Install or Configure Traefik on a Kubernetes Cluster
    """
    context.obj = click.Context(cli)
    context.obj.kubeconfig = kubeconfig


@cli.group()
@click.pass_obj
def install(ctx):
    """
    Install Traefik Helm Chart
    """
    pass


@install.command()
@click.option("--certmanager-values",
              default=str(certmanager_values_default_path),
              type=click.Path(exists=True),
              help="Path to Traefik Helm values file")
@click.pass_obj
def helm_chart(ctx, certmanager_values):
    """
    Install CertManager Helm Chart and Custom Resource Definitions
    """
    InstallCertManagerHelmChart(
        kubeconfig=ctx.kubeconfig,
        certmanager_values=certmanager_values
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