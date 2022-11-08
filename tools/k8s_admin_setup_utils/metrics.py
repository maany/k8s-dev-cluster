from pathlib import Path
import os

import click

from api.core.run_context import kube_proxy
from api.metrics.metrics import InstallKubePrometheusStack, UninstallKubePrometheusStack


kube_prometheus_values_default_path = Path(
    __file__).parent.parent / "config" / "kube-prometheus-values.yaml"



@click.group()
@click.option("--kubeconfig",
              default=f"{os.environ.get('HOME', '~')}/.kube/config",
              type=click.Path(exists=True),
              help="Path to kubeconfig file")
@click.pass_context
def cli(context, kubeconfig):
    """
    Install and Configure Kube Prometheus Stack
    """
    context.obj = click.Context(cli)
    context.obj.kubeconfig = kubeconfig


@cli.command()
@click.option("--kube-prometheus-values", "--values", type=click.Path(exists=True), default=str(kube_prometheus_values_default_path), help="Path to Kube Prometheus Stack Helm values file")
@click.pass_obj
def install(ctx, kube_prometheus_values):
    """
    Install Kube Prometheus Stack
    """
    with kube_proxy(ctx.kubeconfig) as k:
        InstallKubePrometheusStack(
            kubeconfig=ctx.kubeconfig,
            values=kube_prometheus_values
        ).run()


@cli.command()
@click.pass_obj
def uninstall(ctx):
    """
    Uninstall Kube Prometheus Stack
    """
    with kube_proxy(ctx.kubeconfig) as k:
        UninstallKubePrometheusStack(
            kubeconfig=ctx.kubeconfig
        ).run()