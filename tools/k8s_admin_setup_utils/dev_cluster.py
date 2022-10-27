import click
from api.dev_cluster import DevClusterConfiguration
from api.core.run_context import kube_proxy


@click.group()
@click.pass_obj
def cli(ctx):
    """
    Configure the vagrant development cluster post launch
    """
    pass

@cli.command()
@click.pass_obj
def init(ctx):
    """
    Restart coredns and metrics server
    """
    with kube_proxy(ctx.kubeconfig):
        DevClusterConfiguration(kubeconfig=ctx.kubeconfig).run()

