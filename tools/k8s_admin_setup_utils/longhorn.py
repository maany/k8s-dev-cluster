import click
from api.longhorn.longhorn import LonghornConfiguration
from api.core.run_context import kube_proxy


@click.group()
@click.pass_obj
def cli(ctx):
    pass

@cli.command()
@click.pass_obj
def install(ctx):
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        LonghornConfiguration().run()
