# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from postgresql_ldap_sync.matcher import DefaultMatcher
from postgresql_ldap_sync.models import GroupMembers


@pytest.mark.unit
class TestDefaultMatcher:
    """Class to group all the DefaultMatcher tests."""

    @pytest.fixture(scope="class")
    def matcher(self):
        """Matcher object to be used throughout the tests."""
        return DefaultMatcher()

    def test_match_users(self, matcher: DefaultMatcher):
        """Test the matching of users between LDAP and PostgreSQL."""
        ldap_users = ["alice", "brianna", "charlie"]
        psql_users = ["alice", "daniel"]

        matches = matcher.match_users(ldap_users, psql_users)
        matches_dict = {match.name: match for match in matches}

        assert matches_dict["alice"].should_keep
        assert matches_dict["brianna"].should_create
        assert matches_dict["charlie"].should_create
        assert matches_dict["daniel"].should_delete

    def test_match_groups(self, matcher: DefaultMatcher):
        """Test the matching of groups between LDAP and PostgreSQL."""
        ldap_groups = ["application", "canonical", "sdaia"]
        psql_groups = ["application", "internal"]

        matches = matcher.match_groups(ldap_groups, psql_groups)
        matches_dict = {match.name: match for match in matches}

        assert matches_dict["application"].should_keep
        assert matches_dict["canonical"].should_create
        assert matches_dict["internal"].should_delete
        assert matches_dict["sdaia"].should_create

    def test_match_group_memberships(self, matcher: DefaultMatcher):
        """Test the matching of memberships between LDAP and PostgreSQL."""
        ldap_memberships = [
            GroupMembers(group="application", users=["mattermost", "wordpress"]),
            GroupMembers(group="canonical", users=["alice", "brianna", "charlie"]),
            GroupMembers(group="sdaia", users=["daniel"]),
        ]
        psql_memberships = [
            GroupMembers(group="application", users=["mattermost"]),
            GroupMembers(group="internal", users=["operator", "replication"]),
        ]

        matches = matcher.match_group_memberships(ldap_memberships, psql_memberships)
        matches_dict = {f"{match.group_name}-{match.user_name}": match for match in matches}

        assert matches_dict["application-mattermost"].should_keep
        assert matches_dict["application-wordpress"].should_grant
        assert matches_dict["canonical-alice"].should_grant
        assert matches_dict["canonical-brianna"].should_grant
        assert matches_dict["canonical-charlie"].should_grant
        assert matches_dict["internal-operator"].should_revoke
        assert matches_dict["internal-replication"].should_revoke
        assert matches_dict["sdaia-daniel"].should_grant
