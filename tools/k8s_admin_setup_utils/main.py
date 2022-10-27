import click
import logging
from api.core.root_logger import config_root_logger
from api.core.constants import ASCII_ART
from k8s_admin_setup_utils import longhorn
from k8s_admin_setup_utils import dev_cluster


logger = logging.getLogger(__name__)


@click.group()
def cli():
    print(ASCII_ART)


cli.add_command(dev_cluster.cli, name="dev-cluster")
cli.add_command(longhorn.cli, name="longhorn")
