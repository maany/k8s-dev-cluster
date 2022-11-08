from pathlib import Path
import os

import click
from click_params import IPV4_ADDRESS

from api.core.run_context import kube_proxy
from api.monitoring.monitoring import InstallKubePrometheusStack, UninstallKubePrometheusStack


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
@click.option("--control-plane-nodes", "--control-plane", required=True, type=IPV4_ADDRESS, multiple=True, help="Control Plane Node Names")
@click.option("--grafana-user", "-u", default="admin", help="Grafana User Name")
@click.password_option("--grafana-password", "-p", default="admin", help="Grafana Password")
@click.pass_obj
def install(ctx, kube_prometheus_values, control_plane_nodes, grafana_user, grafana_password):
    """
    Install Kube Prometheus Stack
    """
    with kube_proxy(ctx.kubeconfig) as k:
        InstallKubePrometheusStack(
            kubeconfig=ctx.kubeconfig,
            values=kube_prometheus_values,
            control_plane_nodes=control_plane_nodes,
            grafana_user=grafana_user,
            grafana_password=grafana_password
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