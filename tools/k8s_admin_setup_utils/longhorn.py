import click
from api.longhorn.longhorn import InstallLonghorn
from api.core.run_context import kube_proxy
import os

@click.group()
@click.option("--kubeconfig", 
    default=f"{os.environ.get('HOME', '~')}/.kube/config", 
    type=click.Path(exists=True), 
    help="Path to kubeconfig file")
@click.pass_context
def cli(context, kubeconfig):
    """
    Install or Configure Longhorn Storage on a Kubernetes Cluster
    """
    context.obj = click.Context(cli)
    context.obj.kubeconfig = kubeconfig

@cli.command()
@click.pass_obj
def install(ctx):
    """
    Install Longhorn
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        InstallLonghorn(kubeconfig=ctx.kubeconfig).run()
