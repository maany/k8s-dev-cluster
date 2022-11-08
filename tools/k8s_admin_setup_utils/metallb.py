import os
from pathlib import Path

import click
from click_params import IPV4_ADDRESS


from api.core.run_context import kube_proxy
from api.metallb.metallb import InstallMetalLbHelmChart, InstallCustomResources, WatchMetalLbEvents, UninstallMetalLb
from pkg_resources import cleanup_resources


metallb_values_default_path = Path(
    __file__).parent.parent / "config" / "metallb-values.yaml"


@click.group()
@click.option("--kubeconfig",
              default=f"{os.environ.get('HOME', '~')}/.kube/config",
              type=click.Path(exists=True),
              help="Path to kubeconfig file")
@click.pass_context
def cli(context, kubeconfig):
    """
    Install or Configure MetalLB on a Kubernetes Cluster
    """
    context.obj = click.Context(cli)
    context.obj.kubeconfig = kubeconfig


@cli.group()
@click.pass_obj
def install(ctx):
    """
    Install MetalLB
    """
    pass


@install.command()
@click.option("--metallb-values",
              default=str(metallb_values_default_path),
              type=click.Path(exists=True),
              help="Path to Metallb Helm values file")
@click.pass_obj
def helm_chart(ctx, metallb_values):
    """
    Install MetalLB Helm Chart and Custom Resource Definitions
    """
    InstallMetalLbHelmChart(
        kubeconfig=ctx.kubeconfig,
        metallb_values=metallb_values
    ).run()


@install.command()
@click.option("--pool-name",
              default="default",
              help="Name of the pool to use for MetalLB")
@click.option("--start-ip",
              type=IPV4_ADDRESS,
              default="172.16.16.200",
              help="Start IP of the pool to use for MetalLB")
@click.option("--end-ip",
              type=IPV4_ADDRESS,
              default="172.16.16.240",
              help="End IP of the pool to use for MetalLB")
@click.pass_obj
def custom_resources(ctx, pool_name, start_ip, end_ip):
    """
    Configure MetalLB L2Advertisement and AddressPool Custom Resources
    """
    InstallCustomResources(kubeconfig=ctx.kubeconfig,
                           pool_name=pool_name,
                           start_ip=start_ip,
                           end_ip=end_ip).run()


@cli.command()
@click.pass_obj
def uninstall(ctx):
    """
    Uninstall MetalLB CRDs and Custom Resources
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        UninstallMetalLb(
            kubeconfig=ctx.kubeconfig
        ).run()


@cli.command()
@click.pass_obj
def watch(ctx):
    """
    Watch MetalLB events
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        WatchMetalLbEvents().run()