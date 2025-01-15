# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from typing import (
    Iterable,
    Iterator,
)

from .models.group_matches import GroupMatch, GroupMembershipMatch
from .models.group_members import GroupMembers
from .models.user_matches import UserMatch


class DefaultMatcher:
    """Class to match LDAP and PostgreSQL entities."""

    @staticmethod
    def match_users(
        ldap_users: Iterable[str],
        psql_users: Iterable[str],
    ) -> Iterator[UserMatch]:
        """Generate match objects for the users."""
        ldap_users = set(ldap_users)
        psql_users = set(psql_users)

        for user in ldap_users | psql_users:
            yield UserMatch(
                name=user,
                exists_in_ldap=(user in ldap_users),
                exists_in_psql=(user in psql_users),
            )

    @staticmethod
    def match_groups(
        ldap_groups: Iterable[str],
        psql_groups: Iterable[str],
    ) -> Iterator[GroupMatch]:
        """Generate match objects for the groups."""
        ldap_groups = set(ldap_groups)
        psql_groups = set(psql_groups)

        for group in ldap_groups | psql_groups:
            yield GroupMatch(
                name=group,
                exists_in_ldap=(group in ldap_groups),
                exists_in_psql=(group in psql_groups),
            )

    @staticmethod
    def match_group_memberships(
        ldap_memberships: Iterable[GroupMembers],
        psql_memberships: Iterable[GroupMembers],
    ) -> Iterator[GroupMembershipMatch]:
        """Generate match objects for the group memberships."""
        ldap_memberships = {m.group: set(m.users) for m in ldap_memberships}
        psql_memberships = {m.group: set(m.users) for m in psql_memberships}

        groups = ldap_memberships.keys() | psql_memberships.keys()

        for group in groups:
            ldap_users = ldap_memberships.get(group, set())
            psql_users = psql_memberships.get(group, set())

            for user in ldap_users | psql_users:
                yield GroupMembershipMatch(
                    user_name=user,
                    group_name=group,
                    exists_in_ldap=(user in ldap_users),
                    exists_in_psql=(user in psql_users),
                )
