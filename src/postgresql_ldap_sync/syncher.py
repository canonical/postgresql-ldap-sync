# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from typing import Literal

from .clients import BaseLDAPClient, BasePostgreClient
from .matcher import DefaultMatcher

ROLE_ACTIONS = Literal[
    "CREATE",
    "DELETE",
    "KEEP",
]

MEMBERSHIP_ACTIONS = Literal[
    "GRANT",
    "REVOKE",
    "KEEP",
]


class Synchronizer:
    """Class to sync LDAP and PostgreSQL entities."""

    def __init__(
        self,
        ldap_client: BaseLDAPClient,
        psql_client: BasePostgreClient,
        entity_matcher: DefaultMatcher,
    ):
        """Initializes the LDAP - PostgreSQL synchronization class."""
        self._ldap_client = ldap_client
        self._psql_client = psql_client
        self._matcher = entity_matcher

    def sync_users(self, actions: list[ROLE_ACTIONS]) -> None:
        """Sync LDAP users to PostgreSQL filtering by the provided actions."""
        matches = self._matcher.match_users(
            self._ldap_client.search_users(),
            self._psql_client.search_users(),
        )

        for match in matches:
            if match.should_create and "CREATE" in actions:
                self._psql_client.create_user(match.name)
            elif match.should_delete and "DELETE" in actions:
                self._psql_client.delete_user(match.name)
            elif match.should_keep and "KEEP" in actions:
                pass

    def sync_groups(self, actions: list[ROLE_ACTIONS]) -> None:
        """Sync LDAP groups to PostgreSQL filtering by the provided actions."""
        matches = self._matcher.match_groups(
            self._ldap_client.search_groups(),
            self._psql_client.search_groups(),
        )

        for match in matches:
            if match.should_create and "CREATE" in actions:
                self._psql_client.create_group(match.name)
            elif match.should_delete and "DELETE" in actions:
                self._psql_client.delete_group(match.name)
            elif match.should_keep and "KEEP" in actions:
                pass

    def sync_group_memberships(self, actions: list[MEMBERSHIP_ACTIONS]) -> None:
        """Sync LDAP memberships to PostgreSQL filtering by the provided actions."""
        matches = self._matcher.match_group_memberships(
            self._ldap_client.search_group_memberships(),
            self._psql_client.search_group_memberships(),
        )

        for match in matches:
            if match.should_grant and "GRANT" in actions:
                self._psql_client.grant_group_memberships([match.group_name], [match.user_name])
            elif match.should_revoke and "REVOKE" in actions:
                self._psql_client.revoke_group_memberships([match.group_name], [match.user_name])
            elif match.should_keep and "KEEP" in actions:
                pass
