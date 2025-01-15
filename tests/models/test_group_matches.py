# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from postgresql_ldap_sync.models import GroupMatch, GroupMembershipMatch


@pytest.mark.unit
class TestGroupMatch:
    """Class to group all the GroupMatch tests."""

    def test_should_create(self):
        """Test the should_create property of a GroupMatch."""
        match = GroupMatch(
            name="sample-group",
            exists_in_ldap=True,
            exists_in_psql=False,
        )

        assert match.should_create is True
        assert match.should_delete is False
        assert match.should_keep is False

    def test_should_delete(self):
        """Test the should_delete property of a GroupMatch."""
        match = GroupMatch(
            name="sample-group",
            exists_in_ldap=False,
            exists_in_psql=True,
        )

        assert match.should_create is False
        assert match.should_delete is True
        assert match.should_keep is False

    def test_should_keep(self):
        """Test the should_keep property of a GroupMatch."""
        match = GroupMatch(
            name="sample-group",
            exists_in_ldap=True,
            exists_in_psql=True,
        )

        assert match.should_create is False
        assert match.should_delete is False
        assert match.should_keep is True


@pytest.mark.unit
class TestGroupMembershipMatch:
    """Class to group all the GroupMembershipMatch tests."""

    def test_should_grant(self):
        """Test the should_grant property of a GroupMembershipMatch."""
        match = GroupMembershipMatch(
            user_name="sample-user",
            group_name="sample-group",
            exists_in_ldap=True,
            exists_in_psql=False,
        )

        assert match.should_grant is True
        assert match.should_revoke is False
        assert match.should_keep is False

    def test_should_revoke(self):
        """Test the should_revoke property of a GroupMembershipMatch."""
        match = GroupMembershipMatch(
            user_name="sample-user",
            group_name="sample-group",
            exists_in_ldap=False,
            exists_in_psql=True,
        )

        assert match.should_grant is False
        assert match.should_revoke is True
        assert match.should_keep is False

    def test_should_keep(self):
        """Test the should_keep property of a GroupMembershipMatch."""
        match = GroupMembershipMatch(
            user_name="sample-user",
            group_name="sample-group",
            exists_in_ldap=True,
            exists_in_psql=True,
        )

        assert match.should_grant is False
        assert match.should_revoke is False
        assert match.should_keep is True
