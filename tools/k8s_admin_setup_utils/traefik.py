from pathlib import Path
import os

import click

from api.traefik.traefik import (
    InstallTraefikHelmChart, WatchTraefikEvents, GetTraefikLoadBalancerIP,
    UninstallTraefikHelmChart
)
from api.core.run_context import kube_proxy

traefik_values_default_path = Path(
    __file__).parent.parent / "config" / "traefik-values.yaml"


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
    Install Traefik Helm Chart and Middlewares
    """
    pass


@install.command()
@click.option("--traefik-values",
              default=str(traefik_values_default_path),
              type=click.Path(exists=True),
              help="Path to Traefik Helm values file")
@click.pass_obj
def helm_chart(ctx, traefik_values):
    """
    Install Traefik Helm Chart and Custom Resource Definitions
    """
    InstallTraefikHelmChart(
        kubeconfig=ctx.kubeconfig,
        traefik_values=traefik_values
    ).run()


@cli.command()
@click.pass_obj
def watch(ctx):
    """
    Watch Traefik Events
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        WatchTraefikEvents(
            kubeconfig=ctx.kubeconfig
        ).run()


@cli.command()
@click.pass_obj
def loadbalancer_ip(ctx):
    """
    Get Traefik Load Balancer IP
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        GetTraefikLoadBalancerIP(
            kubeconfig=ctx.kubeconfig
        ).run()


@cli.group
@click.pass_obj
def uninstall(ctx):
    """
    Uninstall Traefik
    """
    pass


@uninstall.command()
@click.pass_obj
def helm_chart(ctx):
    """
    Uninstall Traefik Helm Chart
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        UninstallTraefikHelmChart(
            kubeconfig=ctx.kubeconfig
        ).run()
