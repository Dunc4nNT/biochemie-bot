import re
from importlib.metadata import version
from typing import Any, Literal, NamedTuple, Self

__version__: str = version(__name__)


class VersionInfo(NamedTuple):
    """Python formatted VersionInfo."""

    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"] = "final"
    serial: int = 0

    @classmethod
    def from_poetry(cls: type[Self], version_str: str) -> Self:
        """Create a VersionInfo from poetry version format."""  # noqa: DOC201
        match: re.Match[str] | None = re.match(
            r"^(?P<major>0|[1-9]\d*)\."
            r"(?P<minor>0|[1-9]\d*)\."
            r"(?P<micro>0|[1-9]\d*)"
            r"(?:((?P<releaselevel>a|b|rc))(?:(?P<serial>0|[1-9]\d*))?)?$",
            version_str,
        )

        if match is None:
            return cls(0, 0, 0)

        named_groups: dict[str, str | Any] = match.groupdict()

        releaselevel: str | None = named_groups.get("releaselevel")
        match releaselevel:
            case "a":
                releaselevel = "alpha"
            case "b":
                releaselevel = "beta"
            case "rc":
                releaselevel = "candidate"
            case _:
                releaselevel = "final"

        serial_str: str | None = named_groups.get("serial")
        serial: int = int(serial_str) if serial_str is not None else 0

        return cls(
            major=int(named_groups["major"]),
            minor=int(named_groups["minor"]),
            micro=int(named_groups["micro"]),
            releaselevel=releaselevel,
            serial=serial,
        )


version_info: VersionInfo = VersionInfo.from_poetry(__version__)

del VersionInfo, Literal, NamedTuple, Self, version
