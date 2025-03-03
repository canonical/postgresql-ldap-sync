# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod
from typing import Iterable

from ...models import GroupMembers


class BaseLDAPClient(ABC):
    """Base class to interact with an underlying LDAP instance."""

    @abstractmethod
    def search_users(self, from_groups: list[str] | None = None) -> Iterable[str]:
        """Search for LDAP users."""
        raise NotImplementedError()

    @abstractmethod
    def search_groups(self, from_users: list[str] | None = None) -> Iterable[str]:
        """Search for LDAP groups."""
        raise NotImplementedError()

    @abstractmethod
    def search_group_memberships(self) -> Iterable[GroupMembers]:
        """Search for LDAP group memberships."""
        raise NotImplementedError()
