import click
import logging
from api.core.root_logger import config_root_logger
from api.core.constants import ASCII_ART
from k8s_admin_setup_utils import longhorn
from k8s_admin_setup_utils import dev_cluster


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


cli.add_command(dev_cluster.cli, name="dev-cluster")
cli.add_command(longhorn.cli, name="longhorn")
