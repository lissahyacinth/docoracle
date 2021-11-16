import pathlib
from docoracle.blocks.items import ClassBlock, FunctionBlock
from docoracle.blocks.module import ModuleBlock
from docoracle.blocks.package import PackageBlock
from urllib import parse


def _write_class(module_dir: pathlib.Path, class_item: ClassBlock) -> None:
    with open(module_dir / f"{class_item.name}.md") as class_writer:
        class_writer.write(f"# {class_item.name}\n")
        class_writer.write(f"# {class_item.comment_block}\n")


def _render_function(function_item: FunctionBlock) -> str:
    function_description = []
    function_description.append(f"# {function_item.name}")
    function_description.append(f"{function_item.signature}")
    function_description.append(f"## Parameters")
    for param in function_item.signature.parameters:
        function_description.append(f"{param.name} : {param.type}")
        function_description.append(f"\t{param.comment}")
    function_description.append(f"## Description")
    function_description.append(f"{function_item.comment_block}")
    return "\n".join(function_description)


def _generate_pkgfile(root_dir: pathlib.Path, root_package: PackageBlock) -> None:
    modules = []
    for module_name, module in root_package.modules.items():
        modules.append(module_name)
        _generate_module(root_dir, module_name, module)
    with open(root_dir / f"{root_package.name}.md") as root_file:
        root_file.write(f"# {root_package.name} API Documentation \n")
        root_file.write(f"## Modules \n")
        for module_name in modules:
            root_file.write(f'1. [{module_name}]("{parse(module_name)}/mod.md") \n')


def _generate_module(
    root_dir: pathlib.Path, module_name: str, module: ModuleBlock
) -> None:
    module_dir = root_dir / module_name
    module_uri = module_dir / "mod.md"
    classes = []
    functions = []
    for class_item in module.classes():
        classes.append(class_item.name)
        _write_class(module_dir, class_item)
    for function_item in module.functions():
        functions.append(function_item.name)
        _write_function(module_dir, function_item)


def generate_markdown(root_package: PackageBlock) -> None:
    root_dir = pathlib.cwd() / "markdown"
    root_dir.mkdir(exist_okay=True)
    _generate_pkgfile(root_dir, root_package)
    pass
