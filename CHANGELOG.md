# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog][docs-changelog], and the version adheres to [Semantic Versioning][docs-semver].


## Unreleased
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


[changes-0.1.0]: https://github.com/canonical/postgresql-ldap-sync/releases/tag/v0.1.0
[changes-0.2.0]: https://github.com/canonical/postgresql-ldap-sync/compare/v0.1.0...v0.2.0
[changes-0.2.1]: https://github.com/canonical/postgresql-ldap-sync/compare/v0.2.0...v0.2.1
[docs-changelog]: https://keepachangelog.com/en/1.0.0/
[docs-semver]: https://semver.org/spec/v2.0.0.html
