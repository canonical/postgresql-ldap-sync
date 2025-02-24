# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest

from postgresql_ldap_sync.clients import DefaultPostgresClient
from postgresql_ldap_sync.models import GroupMembers


@pytest.mark.integration
class TestDefaultPostgresClient:
    """Class to group all the default PostgresClient tests."""

    @pytest.fixture(scope="class")
    def client(self):
        """Client object to be used throughout the tests."""
        client = DefaultPostgresClient(
            host="0.0.0.0",
            port="5432",
            database=os.environ["POSTGRES_DATABASE"],
            username=os.environ["POSTGRES_USERNAME"],
            password=os.environ["POSTGRES_PASSWORD"],
            auto_commit=False,
        )

        client.create_user("user_1")
        client.create_user("user_2")
        client.create_user("user_3")

        client.create_group("group_1")
        client.create_group("group_2")
        client.create_group("group_3")

        client.grant_group_memberships(["group_1"], ["user_1", "user_2"])
        client.grant_group_memberships(["group_2"], ["user_2", "user_3"])
        client.grant_group_memberships(["group_3"], ["group_1"])

        yield client

        client.close()

    def test_create_user(self, client: DefaultPostgresClient):
        """Test the create_user functionality."""
        client.create_user("john")

        users = client.search_users()
        users = list(users)

        assert "john" in users

    def test_create_group(self, client: DefaultPostgresClient):
        """Test the create_user functionality."""
        client.create_group("group_rw")

        groups = client.search_groups()
        groups = list(groups)

        assert "group_rw" in groups

    def test_search_users_scoped(self, client: DefaultPostgresClient):
        """Test the search_users functionality from a group."""
        users = client.search_users(from_group="group_1")
        users = list(users)

        assert "user_1" in users
        assert "user_2" in users
        assert "user_3" not in users
        assert len(users) == len(set(users))

    def test_search_users_unscoped(self, client: DefaultPostgresClient):
        """Test the search_users functionality from any group."""
        users = client.search_users()
        users = list(users)

        assert "user_1" in users
        assert "user_2" in users
        assert "user_3" in users
        assert len(users) == len(set(users))

    def test_search_groups_scoped(self, client: DefaultPostgresClient):
        """Test the search_groups functionality from a user."""
        groups = client.search_groups(from_user="user_2")
        groups = list(groups)

        assert "group_1" in groups
        assert "group_2" in groups
        assert "group_3" not in groups
        assert len(groups) == len(set(groups))

    def test_search_groups_unscoped(self, client: DefaultPostgresClient):
        """Test the search_groups functionality from any user."""
        groups = client.search_groups()
        groups = list(groups)

        assert "group_1" in groups
        assert "group_2" in groups
        assert "group_3" in groups
        assert len(groups) == len(set(groups))

    def test_search_group_memberships(self, client: DefaultPostgresClient):
        """Test the search_group_memberships functionality."""
        memberships = client.search_group_memberships()
        memberships = [GroupMembers(m.group, list(m.users)) for m in memberships]

        assert GroupMembers("group_1", ["user_1", "user_2"]) in memberships
        assert GroupMembers("group_2", ["user_2", "user_3"]) in memberships
        assert GroupMembers("group_3", ["group_1"]) not in memberships
