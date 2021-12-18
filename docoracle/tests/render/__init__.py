from docoracle.blocks.module import parse_module
from docoracle.blocks.package import create_reference_table
from docoracle.discovery.paths import find_resource_path


if __name__ == "__main__":
    module_path = find_resource_path("docoracle", ["blocks",  "parameters"], None)
    rt, rm = create_reference_table([module_path])
    module_block = parse_module(module_path)
    module_block.link(rt, rm)
    breakpoint()