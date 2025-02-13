# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import itertools
import logging
from typing import Iterator

import psycopg2
from psycopg2.errors import DatabaseError, ProgrammingError
from psycopg2.extras import RealDictCursor, RealDictRow
from psycopg2.sql import SQL, Composable, Identifier

from ...models import GroupMembers
from .base import BasePostgreClient

logger = logging.getLogger()


class DefaultPostgresClient(BasePostgreClient):
    """Class to interact with an underlying PostgreSQL instance."""

    _SYSTEM_ROLES = {
        "pg_checkpoint",
        "pg_create_subscription",
        "pg_database_owner",
        "pg_execute_server_program",
        "pg_monitor",
        "pg_read_all_data",
        "pg_read_all_settings",
        "pg_read_all_stats",
        "pg_read_server_files",
        "pg_signal_backend",
        "pg_stat_scan_tables",
        "pg_use_reserved_connections",
        "pg_write_all_data",
        "pg_write_server_files",
    }

    def __init__(
        self,
        host: str,
        port: str,
        database: str,
        username: str,
        password: str,
        auto_commit: bool = True,
    ):
        """Initialize the psycopg2 internal client."""
        self._client = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            dbname=database,
        )
        self._client.set_session(
            autocommit=auto_commit,
        )

    def _execute_query(self, query: Composable) -> list[RealDictRow]:
        """Execute a SQL query and return the results."""
        with self._client.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(query)
            except DatabaseError as error:
                logger.error(error.pgerror)
                self._client.rollback()
                raise
            else:
                return cursor.fetchall()

    def _create_role(self, role: str, login: bool, inherit: bool) -> None:
        """Create a role in PostgreSQL."""
        quoted_role = Identifier(role)
        quoted_options = " ".join([
            "LOGIN" if login else "NOLOGIN",
            "INHERIT" if inherit else "NOINHERIT",
        ])

        query = SQL(f"CREATE ROLE {{role}} WITH {quoted_options}")
        query = query.format(role=quoted_role)

        try:
            self._execute_query(query)
        except ProgrammingError:
            logger.error(f"Could not create role {quoted_role}")

    def _delete_role(self, role: str) -> None:
        """Delete a role in PostgreSQL."""
        quoted_role = Identifier(role)

        query = SQL("DROP ROLE {role}")
        query = query.format(role=quoted_role)

        try:
            self._execute_query(query)
        except ProgrammingError:
            logger.error(f"Could not delete role {quoted_role}")

    def _grant_role_memberships(self, groups: list[str], users: list[str]) -> None:
        """Grant role membership to a list of roles."""
        quoted_groups = SQL(",").join(Identifier(group) for group in groups)
        quoted_users = SQL(",").join(Identifier(user) for user in users)

        query = SQL("GRANT {groups} TO {users}")
        query = query.format(
            groups=quoted_groups,
            users=quoted_users,
        )

        try:
            self._execute_query(query)
        except ProgrammingError:
            logger.error(f"Could not grant memberships to groups {quoted_groups}")

    def _revoke_role_memberships(self, groups: list[str], users: list[str]) -> None:
        """Revoke role membership from a list of roles."""
        quoted_groups = SQL(",").join(Identifier(group) for group in groups)
        quoted_users = SQL(",").join(Identifier(user) for user in users)

        query = SQL("REVOKE {groups} FROM {users}")
        query = query.format(
            groups=quoted_groups,
            users=quoted_users,
        )
        try:
            self._execute_query(query)
        except ProgrammingError:
            logger.error(f"Could not revoke memberships from groups {quoted_groups}")

    def close(self) -> None:
        """Close the psycopg2 cursor and connection."""
        self._client.close()

    def create_user(self, user: str, login: bool = True, inherit: bool = True) -> None:
        """Create a user in PostgreSQL."""
        self._create_role(user, login, inherit)

    def delete_user(self, user: str) -> None:
        """Delete a user in PostgreSQL."""
        self._delete_role(user)

    def create_group(self, group: str, login: bool = False, inherit: bool = False) -> None:
        """Create a group in PostgreSQL."""
        self._create_role(group, login, inherit)

    def delete_group(self, group: str) -> None:
        """Delete a group in PostgreSQL."""
        self._delete_role(group)

    def grant_group_memberships(self, groups: list[str], users: list[str]) -> None:
        """Grant groups membership to a list of users."""
        self._grant_role_memberships(groups, users)

    def revoke_group_memberships(self, groups: list[str], users: list[str]) -> None:
        """Revoke groups membership from a list of users."""
        self._revoke_role_memberships(groups, users)

    def search_users(self) -> Iterator[str]:
        """Search for PostgreSQL users."""
        query = SQL(
            "SELECT rolname "
            "FROM pg_catalog.pg_roles "
            "WHERE rolcanlogin AND oid IN (SELECT member from pg_catalog.pg_auth_members) "
            "ORDER BY 1"
        )
        rows = self._execute_query(query)

        for row in rows:
            user = row["rolname"]
            if user not in self._SYSTEM_ROLES:
                yield user

    def search_groups(self) -> Iterator[str]:
        """Search for PostgreSQL groups."""
        query = SQL(
            "SELECT rolname "
            "FROM pg_catalog.pg_roles "
            "WHERE rolcanlogin AND oid NOT IN (SELECT member from pg_catalog.pg_auth_members) "
            "ORDER BY 1"
        )
        rows = self._execute_query(query)

        for row in rows:
            group = row["rolname"]
            if group not in self._SYSTEM_ROLES:
                yield group

    def search_group_memberships(self) -> Iterator[GroupMembers]:
        """Search for PostgreSQL group memberships."""
        query = SQL(
            "SELECT roles_2.rolname as group, roles_1.rolname as user "
            "FROM pg_catalog.pg_roles roles_1 "
            "JOIN pg_catalog.pg_auth_members memberships ON (memberships.member=roles_1.oid) "
            "JOIN pg_catalog.pg_roles roles_2 ON (memberships.roleid=roles_2.oid) "
            "WHERE roles_2.rolcanlogin "
            "ORDER BY 1"
        )
        rows = self._execute_query(query)

        group_func = lambda row: row["group"]
        user_func = lambda row: row["user"]

        for group, grouped_rows in itertools.groupby(rows, group_func):
            yield GroupMembers(group=group, users=map(user_func, grouped_rows))
