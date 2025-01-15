# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from dataclasses import dataclass


@dataclass
class GroupMatch:
    """Class to store the LDAP - PostgreSQL group match information."""

    name: str
    exists_in_ldap: bool
    exists_in_psql: bool

    @property
    def should_create(self) -> bool:
        """Whether the group must be created in PostgreSQL."""
        return self.exists_in_ldap and not self.exists_in_psql

    @property
    def should_delete(self) -> bool:
        """Whether the group must be deleted from PostgreSQL."""
        return not self.exists_in_ldap and self.exists_in_psql

    @property
    def should_keep(self) -> bool:
        """Whether the group must be preserved in PostgreSQL."""
        return self.exists_in_ldap and self.exists_in_psql


@dataclass
class GroupMembershipMatch:
    """Class to store the LDAP - PostgreSQL group membership match information."""

    user_name: str
    group_name: str
    exists_in_ldap: bool
    exists_in_psql: bool

    @property
    def should_grant(self) -> bool:
        """Whether the group membership must be granted in PostgreSQL."""
        return self.exists_in_ldap and not self.exists_in_psql

    @property
    def should_revoke(self) -> bool:
        """Whether the group membership must be revoked from PostgreSQL."""
        return not self.exists_in_ldap and self.exists_in_psql

    @property
    def should_keep(self) -> bool:
        """Whether the group membership must be preserved in PostgreSQL."""
        return self.exists_in_ldap and self.exists_in_psql
