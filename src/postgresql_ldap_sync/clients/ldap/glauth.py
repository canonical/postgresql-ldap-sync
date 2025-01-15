# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
from typing import Iterator

import ldap

from ...models import GroupMembers
from .base import BaseLDAPClient

logger = logging.getLogger()


class GLAuthClient(BaseLDAPClient):
    """Class to interact with an underlying GLAuth instance."""

    _REQUIRED_USER_FILTERS = ("(objectClass=posixAccount)",)
    _REQUIRED_GROUP_FILTERS = ("(objectClass=posixGroup)",)

    def __init__(self, host: str, port: str, base_dn: str, bind_username: str, bind_password: str):
        """Initialize the ldap internal client."""
        self._base_dn = base_dn
        self._client = ldap.initialize(f"ldap://{host}:{port}")
        self._client.simple_bind_s(bind_username, bind_password)

    @staticmethod
    def _decode_name(name: bytes) -> str:
        """Decode a name from its byte representation."""
        try:
            return name.decode()
        except UnicodeDecodeError:
            logger.warning(f"Could not decode name '{name}'")
            return ""

    @staticmethod
    def _validate_filters(filters: list[str]) -> None:
        """Validate the query filters format."""
        for f in filters:
            if not f.startswith("(") or not f.endswith(")"):
                raise ValueError("Filters must be wrapped in parenthesis")

    def _build_user_filter(self, filters: list[str]) -> str:
        """Build a user filter string given a range of query filters."""
        self._validate_filters(filters)

        # fmt: off
        return (
            f"(&"
            f"{''.join(self._REQUIRED_USER_FILTERS)}"
            f"{''.join(filters)}"
            f")"
        )

    def _build_group_filter(self, filters: list[str]) -> str:
        """Build a group filter string given a range of query filters."""
        self._validate_filters(filters)

        # fmt: off
        return (
            f"(&"
            f"{''.join(self._REQUIRED_GROUP_FILTERS)}"
            f"{''.join(filters)}"
            f")"
        )

    def search_users(self, filters: list[str] | None = None) -> Iterator[str]:
        """Search for LDAP users."""
        if filters is None:
            filters = []

        filter_str = self._build_user_filter(filters)

        users = self._client.search_s(
            base=self._base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=filter_str,
            attrlist=["cn"],
        )

        for _, user in users:
            yield self._decode_name(user["cn"][0])

    def search_groups(self, filters: list[str] | None = None) -> Iterator[str]:
        """Search for LDAP groups."""
        if filters is None:
            filters = []

        filter_str = self._build_group_filter(filters)

        groups = self._client.search_s(
            base=self._base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=filter_str,
            attrlist=["cn"],
        )

        for _, group in groups:
            yield self._decode_name(group["cn"][0])

    def search_group_memberships(self, filters: list[str] | None = None) -> Iterator[GroupMembers]:
        """Search for LDAP group memberships."""
        if filters is None:
            filters = []

        filter_str = self._build_group_filter(filters)

        memberships = self._client.search_s(
            base=self._base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=filter_str,
            attrlist=["cn", "memberUid"],
        )

        for _, membership in memberships:
            group_name = membership["cn"][0]
            user_names = membership["memberUid"]

            yield GroupMembers(
                group=(self._decode_name(group_name)),
                users=(self._decode_name(user_name) for user_name in user_names),
            )
