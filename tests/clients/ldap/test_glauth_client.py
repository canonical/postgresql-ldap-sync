# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest

from postgresql_ldap_sync.clients import GLAuthClient
from postgresql_ldap_sync.models import GroupMembers


@pytest.mark.integration
class TestGLAuthClient:
    """Class to group all the GLAuthClient tests."""

    @pytest.fixture(scope="class")
    def client(self):
        """Client object to be used throughout the tests."""
        return GLAuthClient(
            host="0.0.0.0",
            port="3893",
            base_dn="dc=glauth,dc=com",
            bind_username=os.environ["GLAUTH_USERNAME"],
            bind_password=os.environ["GLAUTH_PASSWORD"],
        )

    def test_search_users_scoped(self, client: GLAuthClient):
        """Test the search_users functionality from some groups."""
        users = client.search_users(from_groups=["danger"])
        users = list(users)

        assert "danger" in users
        assert "hackers" not in users
        assert "johndoe" not in users
        assert "serviceuser" not in users

    def test_search_users_unscoped(self, client: GLAuthClient):
        """Test the search_users functionality from any group."""
        users = client.search_users()
        users = list(users)

        assert "danger" in users
        assert "hackers" in users
        assert "johndoe" in users
        assert "serviceuser" in users

    def test_search_groups_scoped(self, client: GLAuthClient):
        """Test the search_groups functionality from some users."""
        groups = client.search_groups(from_users=["serviceuser"])
        groups = list(groups)

        assert "danger" not in groups
        assert "superheros" not in groups
        assert "svcaccts" in groups

    def test_search_groups_unscoped(self, client: GLAuthClient):
        """Test the search_groups functionality from any user."""
        groups = client.search_groups()
        groups = list(groups)

        assert "danger" in groups
        assert "superheros" in groups
        assert "svcaccts" in groups

    def test_search_group_memberships(self, client: GLAuthClient):
        """Test the search_group_memberships functionality."""
        memberships = client.search_group_memberships()
        memberships = [GroupMembers(m.group, list(m.users)) for m in memberships]

        assert GroupMembers("danger", ["danger"]) in memberships
        assert GroupMembers("superheros", ["hackers", "johndoe"]) in memberships
        assert GroupMembers("svcaccts", ["serviceuser"]) in memberships
