# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

from unittest.mock import patch

import pytest

from postgresql_ldap_sync.clients import DummyLDAPClient, DummyPostgresClient
from postgresql_ldap_sync.matcher import DefaultMatcher
from postgresql_ldap_sync.models import GroupMembers
from postgresql_ldap_sync.syncher import Synchronizer


@pytest.mark.unit
class TestSynchronizer:
    """Class to group all the Synchronizer tests."""

    @pytest.fixture(scope="class")
    def synchronizer(self):
        """Synchronizer object to be used throughout the tests."""
        ldap_client = DummyLDAPClient(
            users=["alice", "brianna", "charlie"],
            groups=["application", "canonical", "sdaia"],
            memberships=[
                GroupMembers(group="application", users=["mattermost", "wordpress"]),
                GroupMembers(group="canonical", users=["alice", "brianna", "charlie"]),
                GroupMembers(group="sdaia", users=["daniel"]),
            ],
        )
        psql_client = DummyPostgresClient(
            users=["alice", "daniel"],
            groups=["application", "internal"],
            memberships=[
                GroupMembers(group="application", users=["mattermost"]),
                GroupMembers(group="internal", users=["operator", "replication"]),
            ],
        )

        return Synchronizer(
            ldap_client=ldap_client,
            psql_client=psql_client,
            entity_matcher=DefaultMatcher(),
        )

    def test_sync_users(self, synchronizer: Synchronizer):
        """Test the creation / deletion of LDAP users into PostgreSQL."""
        with (
            patch.object(synchronizer._psql_client, "create_user") as create_user,
            patch.object(synchronizer._psql_client, "delete_user") as delete_user,
        ):
            synchronizer.sync_users(actions=["CREATE"])
            create_user.assert_called()
            delete_user.assert_not_called()

            create_user.reset_mock()
            delete_user.reset_mock()

            synchronizer.sync_users(actions=["DELETE"])
            create_user.assert_not_called()
            delete_user.assert_called()

            create_user.reset_mock()
            delete_user.reset_mock()

            synchronizer.sync_users(actions=["CREATE", "DELETE"])
            create_user.assert_called()
            delete_user.assert_called()

    def test_sync_groups(self, synchronizer: Synchronizer):
        """Test the creation / deletion of LDAP groups into PostgreSQL."""
        with (
            patch.object(synchronizer._psql_client, "create_group") as create_group,
            patch.object(synchronizer._psql_client, "delete_group") as delete_group,
        ):
            synchronizer.sync_groups(actions=["CREATE"])
            create_group.assert_called()
            delete_group.assert_not_called()

            create_group.reset_mock()
            delete_group.reset_mock()

            synchronizer.sync_groups(actions=["DELETE"])
            create_group.assert_not_called()
            delete_group.assert_called()

            create_group.reset_mock()
            delete_group.reset_mock()

            synchronizer.sync_groups(actions=["CREATE", "DELETE"])
            create_group.assert_called()
            delete_group.assert_called()

    def test_sync_group_memberships(self, synchronizer: Synchronizer):
        """Test the creation / deletion of LDAP memberships into PostgreSQL."""
        with (
            patch.object(synchronizer._psql_client, "grant_group_membership") as grant_member,
            patch.object(synchronizer._psql_client, "revoke_group_membership") as revoke_member,
        ):
            synchronizer.sync_group_memberships(actions=["GRANT"])
            grant_member.assert_called()
            revoke_member.assert_not_called()

            grant_member.reset_mock()
            revoke_member.reset_mock()

            synchronizer.sync_group_memberships(actions=["REVOKE"])
            grant_member.assert_not_called()
            revoke_member.assert_called()

            grant_member.reset_mock()
            revoke_member.reset_mock()

            synchronizer.sync_group_memberships(actions=["GRANT", "REVOKE"])
            grant_member.assert_called()
            revoke_member.assert_called()
