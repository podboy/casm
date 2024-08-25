# coding:utf-8

import os
from typing import Optional


def ismount(path: str) -> bool:
    """Test whether a path and all its parent paths contain a mount point."""
    realpath: str = os.path.realpath(path)
    while realpath != "/":
        if os.path.ismount(realpath):
            return True
        realpath = os.path.dirname(realpath)
    return False


def mountpoint(path: str) -> Optional[str]:
    realpath: str = os.path.realpath(path)
    while realpath != "/":
        if os.path.ismount(realpath):
            return realpath
        realpath = os.path.dirname(realpath)
    return None
