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
from .podman import disable_service as podman_disable_service
from .podman import enable_service as podman_enable_service
from .podman import stop_service as podman_stop_service
from .podman_compose import podman_compose_cmd

__package_name__ = "casm"
__prog_name__ = "casm"
__prog_compose__ = f"{__prog_name__}-compose"
__version__ = "0.2.alpha.1"

URL_PROG = "https://github.com/podboy/casm"
