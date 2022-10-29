import os
from pathlib import Path

import click

from api.longhorn.longhorn import InstallLonghorn, WatchLonghornEvents, ExposeLonghornUI
from api.core.run_context import kube_proxy

longhorn_values_default_path = Path(
    __file__).parent.parent / "config" / "longhorn-values.yaml"


@click.group()
@click.option("--kubeconfig",
              default=f"{os.environ.get('HOME', '~')}/.kube/config",
              type=click.Path(exists=True),
              help="Path to kubeconfig file")
@click.pass_context
def cli(context, kubeconfig, longhorn_values):
    """
    Install or Configure Longhorn Storage on a Kubernetes Cluster
    """
    context.obj = click.Context(cli)
    context.obj.kubeconfig = kubeconfig


@cli.command()
@click.pass_obj
@click.option("--longhorn-values",
              default=str(longhorn_values_default_path),
              type=click.Path(exists=True),
              help="Path to Longhorn Helm values file")
def install(ctx, longhorn_values):
    """
    Install Longhorn
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        InstallLonghorn(
            kubeconfig=ctx.kubeconfig,
            longhorn_values=longhorn_values
        ).run()


@cli.command()
@click.pass_obj
def watch_events(ctx):
    """
    Watch Longhorn events
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        WatchLonghornEvents(
            kubeconfig=ctx.kubeconfig
        ).run()


@cli.command()
@click.pass_obj
@click.option("--port", default=8000, help="Port to expose longhorn UI")
def expose(ctx, port):
    """
    Expose Longhorn UI on a port ( Default: 8000 )
    """
    with kube_proxy(kubeconfig=ctx.kubeconfig):
        ExposeLonghornUI(ctx.kubeconfig, port).run()
