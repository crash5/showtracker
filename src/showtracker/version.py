'''
Returns the content of the VERSION file.
VERSION file has to be in the source root next to this file.
'''

from importlib import import_module
from pathlib import Path
import importlib.resources as pkg_resources


_UNKNOW_VERSION: str = '0.0.0-non-production-ready'


def _read_text(package, filename) -> str:
    pkg = import_module(package)
    try:
        # from python 3.9
        content = pkg_resources.files(pkg).joinpath(filename).read_text()
    except AttributeError:
        # before python 3.9, fall back to method deprecated in 3.11
        content = pkg_resources.read_text(pkg, filename)

    return content


def version_string() -> str:
    version: str = _UNKNOW_VERSION

    try:
        if pkg_name := __package__:
            # if used as a package
            version = _read_text(pkg_name, 'VERSION')
        else:
            # if not used as a package
            version_file = Path(__file__).parent / 'VERSION'
            version = version_file.read_text()
    except:  # noqa: E722
        # use the default string if we can't read the version
        pass

    return version.strip()
