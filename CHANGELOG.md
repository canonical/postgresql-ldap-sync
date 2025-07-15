# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog][docs-changelog], and the version adheres to [Semantic Versioning][docs-semver].


## Unreleased

## [0.3.2][changes-0.3.2] - 2025-07-15
### Fixed
- Possible crash when deleting a user that owns resources in other databases.

## [0.3.1][changes-0.3.1] - 2025-03-26
### Fixed
- Avoid PostgreSQL `GRANT` and `REVOKE` queries when receiving empty lists.

## [0.3.0][changes-0.3.0] - 2025-03-11
### Added
- Ability to search LDAP users / groups in a scoped manner.
### Fixed
- Possible crash when deleting a user that owns resources.

## [0.2.1][changes-0.2.1] - 2025-02-26
### Added
- Ability to search PostgreSQL users / groups in a scoped manner.

## [0.2.0][changes-0.2.0] - 2025-02-17
### Added
- Ability to grant / revoke role membership in bulk.
### Fixed
- Possible query injection when PG client used in isolation.
- PostgreSQL user and group definitions. Now based on log-in capability.

## [0.1.0][changes-0.1.0] - 2025-02-04
### Added
- Initial functionality.
- Initial test suite.
- Initial documentation.


[changes-0.1.0]: https://github.com/canonical/postgresql-ldap-sync/releases/tag/0.1.0
[changes-0.2.0]: https://github.com/canonical/postgresql-ldap-sync/compare/0.1.0...0.2.0
[changes-0.2.1]: https://github.com/canonical/postgresql-ldap-sync/compare/0.2.0...0.2.1
[changes-0.3.0]: https://github.com/canonical/postgresql-ldap-sync/compare/0.2.1...0.3.0
[changes-0.3.1]: https://github.com/canonical/postgresql-ldap-sync/compare/0.3.0...0.3.1
[changes-0.3.2]: https://github.com/canonical/postgresql-ldap-sync/compare/0.3.1...0.3.2
[docs-changelog]: https://keepachangelog.com/en/1.0.0/
[docs-semver]: https://semver.org/spec/v2.0.0.html
