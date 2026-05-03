import importlib
import pkgutil

import click


def autodiscover_commands(
    group: click.Group,
    package: str,
) -> None:
    """Walk *package* recursively and register every
    :class:`click.BaseCommand` found on the *group*.
    """
    pkg = importlib.import_module(package)
    for _importer, modname, _ispkg in pkgutil.walk_packages(
        pkg.__path__,
        prefix=f"{package}.",
    ):
        mod = importlib.import_module(modname)
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (
                isinstance(attr, click.BaseCommand)  # type: ignore[arg-type]
                and attr is not group
                and attr.name not in (group.commands or {})
            ):
                group.add_command(attr)
