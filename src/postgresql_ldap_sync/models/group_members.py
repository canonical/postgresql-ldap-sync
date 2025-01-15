# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from dataclasses import dataclass
from typing import Iterable


@dataclass
class GroupMembers:
    """Class to store group members together."""

    group: str
    users: Iterable[str]
