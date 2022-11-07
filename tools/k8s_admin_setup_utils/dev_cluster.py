import os

import click
from click_params import IPV4_ADDRESS

from api.dev_cluster import DevClusterConfiguration, InstallCilium, ExposeHubble
from api.core.run_context import kube_proxy

@click.group()
@click.option("--kubeconfig", 
    default=f"{os.environ.get('HOME', '~')}/.kube/config", 
    type=click.Path(exists=True), 
    help="Path to kubeconfig file")
@click.pass_context
def cli(ctx, kubeconfig):
    """
    Configure the vagrant development cluster post launch
    """
    ctx.obj = click.Context(cli)
    ctx.obj.kubeconfig = kubeconfig

@cli.command()
@click.pass_obj
def reload(ctx):
    """
    Restart coredns and metrics server
    """
    with kube_proxy(ctx.kubeconfig):
        DevClusterConfiguration(kubeconfig=ctx.kubeconfig).run()


@cli.group()
@click.pass_obj
def cilium(ctx):
    """
    Configure cilium
    """
    pass

@cilium.command()
@click.option("--kubemaster-ip",
    default="172.16.16.10",
    type=IPV4_ADDRESS,
    help="IP address of the kubemaster")
@click.pass_obj
def install(ctx, kubemaster_ip):
    """
    Install cilium
    """
    with kube_proxy(ctx.kubeconfig):
        InstallCilium(kubeconfig=ctx.kubeconfig, kubemaster_ip=kubemaster_ip).run()


@cilium.command()
@click.pass_obj
def expose(ctx):
    """
    Expose hubble on loadbalancer
    """
    with kube_proxy(ctx.kubeconfig):
        ExposeHubble(kubeconfig=ctx.kubeconfig).run()