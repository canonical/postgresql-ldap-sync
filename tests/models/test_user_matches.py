# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

import pytest

from postgresql_ldap_sync.models import UserMatch


@pytest.mark.unit
class TestUserMatch:
    """Class to group all the UserMatch tests."""

    def test_should_create(self):
        """Test the should_create property of a UserMatch."""
        match = UserMatch(
            name="sample-user",
            exists_in_ldap=True,
            exists_in_psql=False,
        )

        assert match.should_create is True
        assert match.should_delete is False
        assert match.should_keep is False

    def test_should_delete(self):
        """Test the should_delete property of a UserMatch."""
        match = UserMatch(
            name="sample-user",
            exists_in_ldap=False,
            exists_in_psql=True,
        )

        assert match.should_create is False
        assert match.should_delete is True
        assert match.should_keep is False

    def test_should_keep(self):
        """Test the should_keep property of a UserMatch."""
        match = UserMatch(
            name="sample-user",
            exists_in_ldap=True,
            exists_in_psql=True,
        )

        assert match.should_create is False
        assert match.should_delete is False
        assert match.should_keep is True
