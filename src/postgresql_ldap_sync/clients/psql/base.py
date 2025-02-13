# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from abc import ABC, abstractmethod
from typing import Iterable

from ...models import GroupMembers


class BasePostgreClient(ABC):
    """Base class to interact with an underlying PostgreSQL instance."""

    @abstractmethod
    def create_user(self, user: str) -> None:
        """Create a user in PostgreSQL."""
        raise NotImplementedError()

    @abstractmethod
    def delete_user(self, user: str) -> None:
        """Delete a user in PostgreSQL."""
        raise NotImplementedError()

    @abstractmethod
    def create_group(self, group: str) -> None:
        """Create a group in PostgreSQL."""
        raise NotImplementedError()

    @abstractmethod
    def delete_group(self, group: str) -> None:
        """Delete a group in PostgreSQL."""
        raise NotImplementedError()

    @abstractmethod
    def grant_group_memberships(self, groups: list[str], users: list[str]) -> None:
        """Grant groups membership to a list of users."""
        raise NotImplementedError()

    @abstractmethod
    def revoke_group_memberships(self, groups: list[str], users: list[str]) -> None:
        """Revoke groups membership from a list of users."""
        raise NotImplementedError()

    @abstractmethod
    def search_users(self) -> Iterable[str]:
        """Search for PostgreSQL users."""
        raise NotImplementedError()

    @abstractmethod
    def search_groups(self) -> Iterable[str]:
        """Search for PostgreSQL groups."""
        raise NotImplementedError()

    @abstractmethod
    def search_group_memberships(self) -> Iterable[GroupMembers]:
        """Search for PostgreSQL group memberships."""
        raise NotImplementedError()
