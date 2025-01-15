# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from dataclasses import dataclass


@dataclass
class UserMatch:
    """Class to store the LDAP - PostgreSQL user match information."""

    name: str
    exists_in_ldap: bool
    exists_in_psql: bool

    @property
    def should_create(self) -> bool:
        """Whether the user must be created in PostgreSQL."""
        return self.exists_in_ldap and not self.exists_in_psql

    @property
    def should_delete(self) -> bool:
        """Whether the user must be deleted from PostgreSQL."""
        return not self.exists_in_ldap and self.exists_in_psql

    @property
    def should_keep(self) -> bool:
        """Whether the user must be preserved in PostgreSQL."""
        return self.exists_in_ldap and self.exists_in_psql
