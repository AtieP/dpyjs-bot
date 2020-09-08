import re
from datetime import datetime, timedelta
from typing import Dict

import dateutil.parser
import dateutil.tz

from discord.ext import commands


class ISO8601Converter(commands.Converter):
    """Converts a ISO 8601 string into a `datetime.datetime` object."""

    async def convert(
        self,
        ctx: commands.Context,
        iso8601_str: str
    ) -> datetime:
        """Converts a ISO 8601 string into a `datetime.datetime` object."""
        try:
            datetime_obj = dateutil.parser.parse(iso8601_str)
        except ValueError:
            raise commands.errors.BadArgument(
                f"{iso8601_str} is not a valid ISO 8601 string."
            )

        return datetime_obj


class DurationConverter(commands.Converter):
    """
    Converts a duration string into a `datetime.datetime` object.

    Example of a duration string: 1h2m3s
    """

    async def convert(
        self,
        ctx: commands.Context,
        duration_str: str
    ) -> int:
        """
        Converts a duration string into a `datetime.datetime` object.

        Example of a duration string: 1h2m3s
        """
        time_string_regex = re.compile(
            r"(?:(?P<years>\d+)y)?"
            r"(?:(?P<weeks>\d+)w)?"
            r"(?:(?P<hours>\d+)h)?"
            r"(?:(?P<minutes>\d+)m)?"
            r"(?:(?P<seconds>\d+)s)?"
        )
        duration_dict: Dict[str, int] = time_string_regex.match(
            duration_str
        ).groupdict()

        # Convert None to 0, else, convert string to int
        for key, value in duration_dict.items():
            if value is None:
                duration_dict[key] = 0
            else:
                try:
                    duration_dict[key] = int(value)
                except ValueError as e:
                    raise commands.errors.BadArgument(
                        f"{e.__class__.__name__}: {e}"
                    )

        # Now, convert all the items above to seconds
        seconds = 0
        for key in duration_dict.keys():
            if key == "years":
                seconds += duration_dict[key] * 31556952
            elif key == "weeks":
                seconds += duration_dict[key] * 604800
            elif key == "day":
                seconds += duration_dict[key] * 86400
            elif key == "hours":
                seconds += duration_dict[key] * 3600
            elif key == "minutes":
                seconds += duration_dict[key] * 60
            else:
                seconds += duration_dict[key]

        current_time = datetime.now() + timedelta(seconds=seconds)
        return current_time
