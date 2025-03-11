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

    def _build_user_filter(self, groups: list[str]) -> str:
        """Build a user filter string given a range of groups."""
        return (
            f"(&"
            f"{''.join(self._REQUIRED_USER_FILTERS)}"
            f"(|"
            f"{''.join(f'(ou={group})' for group in groups)}"
            f")"
            f")"
        )

    def _build_group_filter(self, users: list[str]) -> str:
        """Build a group filter string given a range of users."""
        return (
            f"(&"
            f"{''.join(self._REQUIRED_GROUP_FILTERS)}"
            f"(|"
            f"{''.join(f'(memberUid={user})' for user in users)}"
            f")"
            f")"
        )

    def search_users(self, from_groups: list[str] | None = None) -> Iterator[str]:
        """Search for LDAP users."""
        if not from_groups:
            from_groups = ["*"]

        filter_str = self._build_user_filter(from_groups)

        users = self._client.search_s(
            base=self._base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=filter_str,
            attrlist=["cn"],
        )

        for _, user in users:
            yield self._decode_name(user["cn"][0])

    def search_groups(self, from_users: list[str] | None = None) -> Iterator[str]:
        """Search for LDAP groups."""
        if not from_users:
            from_users = ["*"]

        filter_str = self._build_group_filter(from_users)

        groups = self._client.search_s(
            base=self._base_dn,
            scope=ldap.SCOPE_SUBTREE,
            filterstr=filter_str,
            attrlist=["cn"],
        )

        for _, group in groups:
            yield self._decode_name(group["cn"][0])

    def search_group_memberships(self) -> Iterator[GroupMembers]:
        """Search for LDAP group memberships."""
        filter_str = self._build_group_filter(["*"])

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
