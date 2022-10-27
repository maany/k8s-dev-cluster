import click
from api.dev_cluster import DevClusterConfiguration
from api.core.run_context import kube_proxy
import os

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
def init(ctx):
    """
    Restart coredns and metrics server
    """
    with kube_proxy(ctx.kubeconfig):
        DevClusterConfiguration(kubeconfig=ctx.kubeconfig).run()

