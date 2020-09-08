import logging
from os import environ
from pathlib import Path
from typing import Optional, Union

import yaml


logger = logging.getLogger(__name__)


def _env_constructor(loader: str, node: str) -> Optional[str]:
    """Implements a custom YAML tag for loading enviroment variables."""
    variable = loader.construct_scalar(node)
    return environ.get(variable)


yaml.SafeLoader.add_constructor("!ENV", _env_constructor)


if not Path("config.yml").exists():
    logger.critical('"config.yml" not found.')
    raise SystemExit

with open("config.yml") as f:
    _CONFIG_FILE = yaml.safe_load(f)


class YAMLGetter(type):
    """A metaclass with a magic method for extracting data from the YAML."""

    subsection = None

    def __getattr__(cls, name: str) -> Union[str, int, float, list, dict]:
        """
        Returns something from the YAML config file.
        """
        try:
            if cls.subsection is not None:
                return _CONFIG_FILE[cls.section][cls.subsection][name]
            else:
                return _CONFIG_FILE[cls.section][name]
        except KeyError:
            logger.error(
                f'Name "{name}" or subsection "{cls.subsection}" or section '
                f'"{cls.section}" not found.'
            )


# Note: these variables are just hints
class Bot(metaclass=YAMLGetter):
    section = "bot"

    prefix: str
    token: str
    owners: list


class Colors(metaclass=YAMLGetter):
    section = "style"
    subsection = "colors"

    red: int
    orange: int
    green: int
    default: int


class Emojis(metaclass=YAMLGetter):
    section = "style"
    subsection = "emojis"

    status_online: str
    status_idle: str
    status_dnd: str
    status_offline: str


class Roles(metaclass=YAMLGetter):
    section = "server"
    subsection = "roles"

    owner: int
    admins: int
    moderators: int
    staff: int
    trial_staff: int
    core_developers: int
    muted: int
    user_bot: int
    bot_testers: int
    human: int
    announcements: int


class WhitelistedFileExtensions(metaclass=YAMLGetter):
    section = "server"
    subsection = "whitelisted_file_extensions"

    whitelist: list


class Channels(metaclass=YAMLGetter):
    section = "server"
    subsection = "channels"
