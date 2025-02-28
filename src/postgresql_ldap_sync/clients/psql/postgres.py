# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import itertools
import logging
from typing import Iterator

import psycopg2
from psycopg2.errors import DatabaseError, ProgrammingError
from psycopg2.extras import RealDictCursor, RealDictRow
from psycopg2.sql import SQL, Composable, Identifier, Literal

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
        self.username = username

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

    def _execute_query(self, query: Composable) -> None:
        """Execute a SQL query and return the results."""
        with self._client.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(query)
            except DatabaseError as error:
                logger.error(error)
                self._client.rollback()
                raise

    def _fetch_results(self, query: Composable) -> list[RealDictRow]:
        """Execute a SQL query and return the results."""
        with self._client.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(query)
            except DatabaseError as error:
                logger.error(error)
                self._client.rollback()
                raise
            else:
                return cursor.fetchall()

    def _create_role(self, role: str, inherit: bool, login: bool) -> None:
        """Create a role in PostgreSQL."""
        quoted_role = Identifier(role)
        quoted_options = " ".join([
            "INHERIT" if inherit else "NOINHERIT",
            "LOGIN" if login else "NOLOGIN",
        ])

        query = SQL(f"CREATE ROLE {{role}} WITH {quoted_options}")
        query = query.format(role=quoted_role)

        try:
            self._execute_query(query)
        except ProgrammingError:
            logger.error(f"Could not create role {quoted_role}")

    def _delete_role(self, role: str) -> None:
        """Delete a role in PostgreSQL."""
        quoted_delete_role = Identifier(role)
        quoted_system_role = Identifier(self.username)

        query_1 = SQL("REASSIGN OWNED BY {delete_role} TO {system_role}").format(
            delete_role=quoted_delete_role,
            system_role=quoted_system_role,
        )
        query_2 = SQL("DROP OWNED BY {role}").format(role=quoted_delete_role)
        query_3 = SQL("DROP ROLE {role}").format(role=quoted_delete_role)

        try:
            self._execute_query(query_1)
            self._execute_query(query_2)
            self._execute_query(query_3)
        except ProgrammingError:
            logger.error(f"Could not delete role {quoted_delete_role}")

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

    def create_user(self, user: str, inherit: bool = True) -> None:
        """Create a user in PostgreSQL."""
        self._create_role(user, inherit=inherit, login=True)

    def delete_user(self, user: str) -> None:
        """Delete a user in PostgreSQL."""
        self._delete_role(user)

    def create_group(self, group: str, inherit: bool = False) -> None:
        """Create a group in PostgreSQL."""
        self._create_role(group, inherit=inherit, login=False)

    def delete_group(self, group: str) -> None:
        """Delete a group in PostgreSQL."""
        self._delete_role(group)

    def grant_group_memberships(self, groups: list[str], users: list[str]) -> None:
        """Grant groups membership to a list of users."""
        self._grant_role_memberships(groups, users)

    def revoke_group_memberships(self, groups: list[str], users: list[str]) -> None:
        """Revoke groups membership from a list of users."""
        self._revoke_role_memberships(groups, users)

    def search_users(self, from_group: str | None = None) -> Iterator[str]:
        """Search for PostgreSQL users."""
        if from_group:
            group_filter = SQL("pg_group.groname LIKE {group}")
            group_regex = Literal(from_group)
        else:
            group_filter = SQL("pg_group.groname LIKE {group} OR pg_group.groname IS NULL")
            group_regex = Literal("%")

        query = SQL(
            "SELECT DISTINCT pg_user.usename "
            "FROM pg_catalog.pg_user "
            "LEFT JOIN pg_catalog.pg_auth_members ON (pg_auth_members.member=pg_user.usesysid) "
            "LEFT JOIN pg_catalog.pg_group ON (pg_auth_members.roleid=pg_group.grosysid) "
            "WHERE {group_filter} "
            "ORDER BY 1"
        )

        query = query.format(group_filter=group_filter.format(group=group_regex))
        rows = self._fetch_results(query)

        for row in rows:
            user = row["usename"]
            if user not in self._SYSTEM_ROLES:
                yield user

    def search_groups(self, from_user: str | None = None) -> Iterator[str]:
        """Search for PostgreSQL groups."""
        if from_user:
            user_filter = SQL("pg_user.usename LIKE {user}")
            user_regex = Literal(from_user)
        else:
            user_filter = SQL("pg_user.usename LIKE {user} OR pg_user.usename IS NULL")
            user_regex = Literal("%")

        query = SQL(
            "SELECT DISTINCT pg_group.groname "
            "FROM pg_catalog.pg_group "
            "LEFT JOIN pg_catalog.pg_auth_members ON (pg_auth_members.roleid=pg_group.grosysid) "
            "LEFT JOIN pg_catalog.pg_user ON (pg_auth_members.member=pg_user.usesysid) "
            "WHERE {user_filter} "
            "ORDER BY 1"
        )

        query = query.format(user_filter=user_filter.format(user=user_regex))
        rows = self._fetch_results(query)

        for row in rows:
            group = row["groname"]
            if group not in self._SYSTEM_ROLES:
                yield group

    def search_group_memberships(self) -> Iterator[GroupMembers]:
        """Search for PostgreSQL group memberships."""
        query = SQL(
            "SELECT pg_group.groname, pg_user.usename "
            "FROM pg_catalog.pg_user "
            "JOIN pg_catalog.pg_auth_members ON (pg_auth_members.member=pg_user.usesysid) "
            "JOIN pg_catalog.pg_group ON (pg_auth_members.roleid=pg_group.grosysid) "
            "ORDER BY 1, 2"
        )
        rows = self._fetch_results(query)

        group_func = lambda row: row["groname"]
        user_func = lambda row: row["usename"]

        for group, grouped_rows in itertools.groupby(rows, group_func):
            if group not in self._SYSTEM_ROLES:
                yield GroupMembers(group=group, users=map(user_func, grouped_rows))
