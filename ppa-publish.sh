#!/bin/bash

# Exit on error
set -eo pipefail

# Mandatory environment variables
if [ -z "${DEBEMAIL}" || -z "${DEBFULLNAME}" ]; then
  echo "Environment variables `DEBEMAIL` and `DEBFULLNAME` must be set"
  exit 1
fi

# Mandatory building packages
if [ -z $(command -v dh) || -z $(command -v dch) || -z $(command -v dput) || -z $(command -v dpkg-buildpackage) ]
  echo "Packages `build-essential`, `devscripts` and `dh-make` must be installed"
  exit 1
fi

# Mandatory CLI tools
if [ -z $(command -v poetry) ]
  echo "CLI utility `poetry` must be installed"
  exit 1
fi

PACKAGE_INFO=$(poetry version)
PACKAGE_NAME="$(echo ${PACKAGE_INFO} | cut -d ' ' -f1)"
PACKAGE_VERSION="$(echo ${PACKAGE_INFO} | cut -d ' ' -f2)"

# Create CHANGELOG file
dch --create \
  --force-distribution \
  --distribution plucky \
  --package "${PACKAGE_NAME}" \
  --newversion "${PACKAGE_VERSION}-0ubuntu1"

uscan --download-current-version

# Build new package
dpkg-buildpackage -sa \
  --no-check-builddeps \
  --build=source \
  --force-sign

# Upload new package
dput "ppa:data-platform/${PACKAGE_NAME}" \
  "../${PACKAGE_NAME}_*_source.changes"
