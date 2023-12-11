# coding:utf-8

from .assemble import assemble_file
from .compose import compose_file
from .compose import compose_network
from .compose import compose_networks
from .compose import compose_service
from .compose import compose_services
from .compose import compose_volume
from .compose import compose_volumes
from .compose import service_volume
from .compose import service_volumes
from .podman import podman_cmd
from .podman_compose import podman_compose_cmd

__package_name__ = "casm"
__prog_name__ = "casm"
__prog_compose__ = f"{__prog_name__}-compose"
__version__ = "0.2"

URL_PROG = "https://github.com/podboy/casm"
