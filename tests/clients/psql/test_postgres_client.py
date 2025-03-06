# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import os

import pytest
from psycopg2.sql import SQL, Literal

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

    @staticmethod
    def _fetch_table_owner(client: DefaultPostgresClient, table_name: str) -> str:
        """Helper function to fetch the ownership of a particular table."""
        table_owner = client._fetch_results(
            SQL("SELECT tableowner FROM pg_tables WHERE tablename = {table_name}").format(
                table_name=Literal(table_name)
            )
        )

        return table_owner[0]["tableowner"]

    def test_create_user(self, client: DefaultPostgresClient):
        """Test the create_user functionality."""
        client.create_user("john")

        users = client.search_users()
        users = list(users)
        assert "john" in users

    def test_delete_user_without_ownership(self, client: DefaultPostgresClient):
        """Test the delete_user functionality when the user does not own a resource."""
        user_name = "user_deleted_without_ownership"

        client.create_user(user_name)
        client.delete_user(user_name)

        users = client.search_users()
        users = list(users)
        assert user_name not in users

    def test_delete_user_with_ownership(self, client: DefaultPostgresClient):
        """Test the delete_user functionality when the user does own a resource."""
        user_name = "user_deleted_with_ownership"

        client.create_user(user_name)
        client._execute_query(SQL("CREATE TABLE user_table (id SERIAL)"))
        client._execute_query(SQL(f"ALTER TABLE user_table OWNER TO {user_name}"))
        client.delete_user(user_name)

        owner = self._fetch_table_owner(client, "user_table")
        assert owner == client.username

        users = client.search_users()
        users = list(users)
        assert user_name not in users

    def test_create_group(self, client: DefaultPostgresClient):
        """Test the create_user functionality."""
        client.create_group("group_rw")

        groups = client.search_groups()
        groups = list(groups)
        assert "group_rw" in groups

    def test_delete_group_without_ownership(self, client: DefaultPostgresClient):
        """Test the delete_group functionality when the group does own a resource."""
        group_name = "group_deleted_without_ownership"

        client.create_group(group_name)
        client.delete_group(group_name)

        groups = client.search_groups()
        groups = list(groups)
        assert group_name not in groups

    def test_delete_group_with_ownership(self, client: DefaultPostgresClient):
        """Test the delete_group functionality when the group does own a resource."""
        group_name = "group_deleted_with_ownership"

        client.create_group(group_name)
        client._execute_query(SQL("CREATE TABLE group_table (id SERIAL)"))
        client._execute_query(SQL(f"ALTER TABLE group_table OWNER TO {group_name}"))
        client.delete_group(group_name)

        owner = self._fetch_table_owner(client, "group_table")
        assert owner == client.username

        groups = client.search_groups()
        groups = list(groups)
        assert group_name not in groups

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
