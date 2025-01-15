# PostgreSQL-LDAP Sync

[![CI/CD Status][ci-status-badge]][ci-status-link]
[![Coverage Status][cov-status-badge]][cov-status-link]
[![Apache license][apache-license-badge]][apache-license-link]

LDAP is often used for a centralized user and role management in an enterprise environment.
PostgreSQL offers LDAP as one of its authentication methods, but the users must already exist in the database,
before the authentication can be used. There is currently no direct authorization of database users on LDAP,
so roles and memberships have to be administered twice.

This program helps to solve the issue by synchronizing users, groups and their memberships from LDAP to PostgreSQL,
where access to LDAP is read-only.

It is meant to run as a cron job.


## 🧑‍💻 Usage

1. Install the package from PyPi:
   ```shell
   pip install postgresql-ldap-sync
   ```

2. Import and build the Synchronizer object:
   ```python
   from postgresql_ldap_sync.clients import DefaultPostgresClient
   from postgresql_ldap_sync.clients import GLAuthClient
   from postgresql_ldap_sync.matcher import DefaultMatcher
   from postgresql_ldap_sync.syncher import Synchronizer

   ldap_client = GLAuthClient(...)
   psql_client = DefaultPostgresClient(...)
   matcher = DefaultMatcher(...)

   syncher = Synchronizer(
       ldap_client=ldap_client,
       psql_client=psql_client,
       entity_matcher=matcher,
   )
   ```

3. Define the actions the synchronizer is allowed to take:
   ```python
   user_actions = ["CREATE", "KEEP"]
   group_actions = ["CREATE", "KEEP"]
   member_actions = ["GRANT", "REVOKE", "KEEP"]
   ```

4. Run the synchronizer, as a cron-job:
   ```python
   import time

   while True:
       syncher.sync_users(user_actions)
       syncher.sync_groups(group_actions)
       syncher.sync_group_memberships(member_actions)
       time.sleep(30)
   ```


## 🔧 Development

### Dependencies
In order to install all the development packages:

```shell
poetry install --all-extras
```

### Linting
All Python files are linted using [Ruff][docs-ruff], to run it:

```shell
tox -e lint
```

### Testing
Project testing is performed using [Pytest][docs-pytest], to run them:

```shell
tox -e unit
```

```shell
export GLAUTH_USERNAME="..."
export GLAUTH_PASSWORD="..."
export POSTGRES_DATABASE="..."
export POSTGRES_USERNAME="..."
export POSTGRES_PASSWORD="..."

podman-compose -f compose.yaml up --detach && tox -e integration
podman-compose -f compose.yaml down
```

### Release
Commits can be tagged to create releases of the package, in order to do so:

1. Bump up the version within the `pyproject.toml` file.
2. Add a new section to the `CHANGELOG.md`.
3. Commit + push the changes.
4. Trigger the [release workflow][github-workflows].


## 🧡 Acknowledges

This project is a Python port of the popular [pg-ldap-sync][github-pg-ldap-sync] Ruby project.


[apache-license-badge]: https://img.shields.io/badge/License-Apache%202.0-blue.svg
[apache-license-link]: https://github.com/canonical/postgresql-ldap-sync/blob/main/LICENSE
[ci-status-badge]: https://github.com/canonical/postgresql-ldap-sync/actions/workflows/ci.yaml/badge.svg?branch=main
[ci-status-link]: https://github.com/canonical/postgresql-ldap-sync/actions/workflows/ci.yaml?query=branch%3Amain
[cov-status-badge]: https://codecov.io/gh/canonical/postgresql-ldap-sync/branch/main/graph/badge.svg
[cov-status-link]: https://codecov.io/gh/canonical/postgresql-ldap-sync

[docs-pytest]: https://docs.pytest.org/en/latest/#
[docs-ruff]: https://docs.astral.sh/ruff/
[github-pg-ldap-sync]: https://github.com/larskanis/pg-ldap-sync
[github-workflows]: https://github.com/canonical/postgresql-ldap-sync/actions/workflows/release.yaml
