# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from ...models import GroupMembers
from .base import BasePostgreClient


class DummyPostgresClient(BasePostgreClient):
    """Class to simplify the testing of other components."""

    def __init__(self, users: list[str], groups: list[str], memberships: list[GroupMembers]):
        """Save arguments as return objects."""
        self._users = users
        self._groups = groups
        self._group_memberships = memberships

    def create_user(self, user: str) -> None:
        """Create a user in PostgreSQL."""
        return None

    def delete_user(self, user: str) -> None:
        """Delete a user in PostgreSQL."""
        return None

    def create_group(self, group: str) -> None:
        """Create a group in PostgreSQL."""
        return None

    def delete_group(self, group: str) -> None:
        """Delete a group in PostgreSQL."""
        return None

    def grant_group_memberships(self, groups: list[str], users: list[str]) -> None:
        """Grant groups membership to a list of users."""
        return None

    def revoke_group_memberships(self, groups: list[str], users: list[str]) -> None:
        """Revoke groups membership from a list of users."""
        return None

    def search_users(self) -> list[str]:
        """Search for PostgreSQL users."""
        return self._users

    def search_groups(self) -> list[str]:
        """Search for PostgreSQL groups."""
        return self._groups

    def search_group_memberships(self) -> list[GroupMembers]:
        """Search for PostgreSQL group memberships."""
        return self._group_memberships
