import pathlib

from typing import List, Dict, Tuple, Set, Optional
from importlib.metadata import requires, packages_distributions, version, distribution
from functools import lru_cache
from dataclasses import dataclass


@dataclass
class UninitializedPackageBlock:
    name: str
    version: version
    location: Optional[pathlib.Path]


def simple_requires(package: str) -> List[str]:
    return list(filter(lambda x: ";" not in x, requires(package)))


def installed_packages() -> Set[str]:
    return set(map(lambda x: x[0], packages_distributions().values()))


def _add_version(package: str) -> Tuple[str, version]:
    return (package, version(package))


def _find_location(package_name: str) -> Optional[pathlib.Path]:
    return next(
        map(
            lambda x: x.locate().parent,
            filter(
                lambda x: str(x)
                in [f"{package_name}/__init__.py", f"site-packages/{package_name}.py"],
                distribution(package_name).files,
            ),
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
    packages = map(parse_package_block, map(_add_version, installed_packages()))
    return {package.name: package for package in packages}
