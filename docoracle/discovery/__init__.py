import sys
import itertools

from typing import List, Dict, Tuple, Set, Optional
from importlib.metadata import requires, packages_distributions, version, distribution
from functools import lru_cache
from dataclasses import dataclass
from importlib.machinery import ModuleSpec


@dataclass
class UninitializedPackageBlock:
    name: str
    version: version
    location: Optional[ModuleSpec]


def simple_requires(package: str) -> List[str]:
    return list(filter(lambda x: ";" not in x, requires(package)))


def installed_packages() -> Set[str]:
    return set(map(lambda x: x[0], packages_distributions().values()))


def _add_version(package: str) -> Tuple[str, version]:
    return (package, version(package))


def _find_location(package_name: str) -> Optional[ModuleSpec]:
    return next(
        filter(
            lambda x: x is not None,
            (meta.find_spec(package_name) for meta in sys.meta_path),
        ),
        None,
    )


def parse_package_block(package: Tuple[str, version]) -> UninitializedPackageBlock:
    package_name, version = package
    return UninitializedPackageBlock(
        name=package_name, version=version, location=_find_location(package_name)
    )


@lru_cache()
def get_local_packages() -> Dict[str, UninitializedPackageBlock]:
    packages = map(
        parse_package_block,
        itertools.chain(
            map(_add_version, installed_packages()),
            ((x, None) for x in sys.stdlib_module_names),
        ),
    )
    return {package.name: package for package in packages}
