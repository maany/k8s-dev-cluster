from pathlib import Path
import os

import click

from api.traefik.traefik import (
    InstallTraefikHelmChart, InstallTraefikDefaultHeaders, InstallTraefikDashboard,
    WatchTraefikEvents, GetTraefikLoadBalancerIP,
    UninstallTraefikHelmChart, UninstallTraefikDefaultHeaders, UninstallTraefikNamespace
)
from api.core.run_context import kube_proxy

traefik_values_default_path = Path(
    __file__).parent.parent / "config" / "traefik-values.yaml"

traefik_default_headers_default_path = Path(
    __file__).parent.parent / "config" / "traefik-default-headers.yaml"


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


@install.command()
@click.option("--traefik-default-headers",
                default=str(traefik_default_headers_default_path),
                type=click.Path(exists=True),
                help="Path to Traefik Defautl Headers file")
@click.pass_obj
def default_headers(ctx, traefik_default_headers):
    """
    Install Traefik Default Headers
    """
    with kube_proxy(ctx.kubeconfig) as k:
        InstallTraefikDefaultHeaders(
            kubeconfig=ctx.kubeconfig,
            traefik_default_headers=traefik_default_headers
        ).run()

@install.command()
@click.option("--username", "-u", required=True, help="Username for Traefik Dashboard")
@click.password_option(help="Password for Traefik Dashboard")
@click.option("--hostname", "-h", default='traefik.local.devmaany.com', help="Hostname for Traefik Dashboard for Ingress + Certs")
@click.pass_obj
def dashboard(ctx, username, password, hostname):
    """
    Install Dashboard
    """
    with kube_proxy(ctx.kubeconfig) as k:
        InstallTraefikDashboard(
            kubeconfig=ctx.kubeconfig,
            dashboard_username=username,
            dashboard_password=password,
            hostname=hostname
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

@uninstall.command()
@click.option("--traefik-default_headers",
                default=str(traefik_default_headers_default_path),
                type=click.Path(exists=True),
                help="Path to Traefik default_headers file")
@click.pass_obj
def default_headers(ctx, traefik_default_headers):
    """
    Uninstall Traefik default_headerss
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        UninstallTraefikDefaultHeaders(
            kubeconfig=ctx.kubeconfig,
            traefik_default_headers=traefik_default_headers
        ).run()

@uninstall.command()
@click.pass_obj
def namespace(ctx):
    """
    Uninstall Dashboard, Secrets, IngressRoutes, Middlewares, and Traefik Namespace
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        UninstallTraefikNamespace(
            kubeconfig=ctx.kubeconfig
        ).run()