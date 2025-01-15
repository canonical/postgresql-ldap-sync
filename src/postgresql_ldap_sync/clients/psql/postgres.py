# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import itertools
import logging
from typing import Iterator

import psycopg2
from psycopg2.errors import DatabaseError, ProgrammingError
from psycopg2.extras import RealDictCursor, RealDictRow

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

    def _execute_query(self, query: str) -> list[RealDictRow]:
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

    def _create_role(self, role: str, options: str) -> None:
        """Create a role in PostgreSQL."""
        query = f"CREATE ROLE {role} {options}"

        try:
            self._execute_query(query)
        except ProgrammingError:
            logger.error(f"Could not create role '{role}'")

    def _delete_role(self, role: str) -> None:
        """Delete a role in PostgreSQL."""
        query = f"DROP ROLE {role}"

        try:
            self._execute_query(query)
        except ProgrammingError:
            logger.error(f"Could not delete role '{role}'")

    def _grant_role_membership(self, role: str, roles: list[str], options: str) -> None:
        """Grant role membership to a list of roles."""
        roles = ",".join(roles)
        query = f"GRANT {role} TO {roles} {options}"

        try:
            self._execute_query(query)
        except ProgrammingError:
            logger.error(f"Could not grant memberships to role '{role}'")

    def _revoke_role_membership(self, role: str, roles: list[str]) -> None:
        """Revoke role membership from a list of roles."""
        roles = ",".join(roles)
        query = f"REVOKE {role} FROM {roles}"

        try:
            self._execute_query(query)
        except ProgrammingError:
            logger.error(f"Could not revoke memberships from role '{role}'")

    def close(self) -> None:
        """Close the psycopg2 cursor and connection."""
        self._client.close()

    def create_user(self, user: str, options: str = "LOGIN") -> None:
        """Create a user in PostgreSQL."""
        self._create_role(user, options)

    def delete_user(self, user: str) -> None:
        """Delete a user in PostgreSQL."""
        self._delete_role(user)

    def create_group(self, group: str, options: str = "NOLOGIN") -> None:
        """Create a group in PostgreSQL."""
        self._create_role(group, options)

    def delete_group(self, group: str) -> None:
        """Delete a group in PostgreSQL."""
        self._delete_role(group)

    def grant_group_membership(self, group: str, users: list[str], options: str = "") -> None:
        """Grant group membership to a list of users."""
        self._grant_role_membership(group, users, options)

    def revoke_group_membership(self, group: str, users: list[str]) -> None:
        """Revoke group membership from a list of users."""
        self._revoke_role_membership(group, users)

    def search_users(self) -> Iterator[str]:
        """Search for PostgreSQL users."""
        query = (
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
        query = (
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
        query = (
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
