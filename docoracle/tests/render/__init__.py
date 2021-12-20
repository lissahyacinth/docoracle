import pathlib

from docoracle.blocks.module import ModuleBlock, parse_module
from docoracle.blocks.package import create_reference_table
from docoracle.discovery.paths import find_resource_path

def render(
    base_dir: pathlib.Path,
    module_block: ModuleBlock
):
    assert base_dir.is_dir()
    assert module_block.name is not None
    module_dir = base_dir / module_block.name
    module_dir.mkdir(exist_ok=True, parents=True)



if __name__ == "__main__":
    # TODO: Find all resource paths in initial package
    module_path = find_resource_path("docoracle", ["blocks",  "parameters"], None)
    rt, rm = create_reference_table([module_path])
    module_block = parse_module(module_path)
    module_block.link(rt, rm)
    breakpoint()