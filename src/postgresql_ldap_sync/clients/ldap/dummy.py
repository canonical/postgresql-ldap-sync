# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from ...models import GroupMembers
from .base import BaseLDAPClient


class DummyLDAPClient(BaseLDAPClient):
    """Class to simplify the testing of other components."""

    def __init__(self, users: list[str], groups: list[str], memberships: list[GroupMembers]):
        """Save arguments as return objects."""
        self._users = users
        self._groups = groups
        self._group_memberships = memberships

    def search_users(self, _: list[str] | None = None) -> list[str]:
        """Search for LDAP users."""
        return self._users

    def search_groups(self, _: list[str] | None = None) -> list[str]:
        """Search for LDAP groups."""
        return self._groups

    def search_group_memberships(self) -> list[GroupMembers]:
        """Search for LDAP group memberships."""
        return self._group_memberships
