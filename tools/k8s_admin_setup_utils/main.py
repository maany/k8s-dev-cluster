from email.policy import default
import click
import logging
from api.core.root_logger import config_root_logger
from api.init_cluster import DevClusterConfiguration
from api.core.run_context import kube_proxy
from api.core.constants import ASCII_ART


logger = logging.getLogger(__name__)

class Context():
    def __init__(self, kubeconfig, verbosity):
        self.kubeconfig = kubeconfig
        self.verbosity = verbosity

@click.group()
@click.option('--verbose', '-v',
              default=0,
              count=True,
              help="Set verbosity level. Select between -v, -vv or -vvv.")
@click.option('--kubeconfig', '-c',
              type=click.Path(exists=True),
              help="Path to kubeconfig file")
@click.pass_context
def cli(ctx, verbose, kubeconfig):
    ctx.obj = Context(kubeconfig, verbose)
    config_root_logger(verbose)
    print(ASCII_ART)


@cli.command()
@click.pass_obj
def init(ctx):
    """
    Initialize the development cluster on Vagrant VMs. This command will
    restart coredns and metrics server pods.
    """
    with kube_proxy(ctx.kubeconfig):
        DevClusterConfiguration(kubeconfig=ctx.kubeconfig).run()
