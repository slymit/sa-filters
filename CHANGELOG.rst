Release Notes
=============

Here you can see the full list of changes between sa-filters
versions, where semantic versioning is used: *major.minor.patch*.


2.1.0
-----

Released 2026-01-30

* Bump pypa/gh-action-pypi-publish from 1.5.0 to 1.13.0
* Migrate tox.ini and setup.py to pyproject.toml
* Fix grammar in README
* Migrate license metadata to PEP 639 style
* Set skip_install for py37 and py38
* Bump actions/setup-python from 5 to 6
* Bump actions/checkout from 4 to 6
* Add Dependabot
* Fix minimum version of sqlalchemy in install_requires
* Add support for Python 3.13 and 3.14
* Bump psycopg2
* Fix error in CI: The version '3.7' with architecture 'x64' was not found for Ubuntu 24.04

2.0.0
-----

Released 2024-06-16

* Modify function apply_pagination api
* Rewrite the README using SQLAlchemy 2.0 style, fix typos and links
* Rename the param 'query' to 'stmt' in functions apply_filters, apply_loads and apply_sort
* Rename variables in tests
* Add python 3.12 support
* Add typing and improve docstrings for public functions
* Add tests for python 3.11
* Add containers target to Makefile
* Add 'downloads' badge
* Fix TypeError: 'type' object is not subscriptable if using python versions 3.7 or 3.8
* Fixed coverage for Python 3.11
* Bump postgres and mysql dev containers to the latest version
* Bump psycopg2 to the version 2.9.9
* Bump GitHub Action Setup Python to v5 and Checkout to v4

1.3.0
-----

Released 2023-07-28

* Add support sqlalchemy 2.0
* Fix CI error 'Failed to initialize container mariadb:latest'
* Fix CI work with latest tox version

1.2.0
-----

Released 2022-11-06

* Add the ability to use table name instead of model name

1.1.0
-----

Released 2022-06-05

* Add the ability to use apply_filters, apply_loads, apply_sort and apply_pagination
  with SQLAlchemy Select object
* Add missing quote in README.rst
* Rewrite tests using a Select object

1.0.0
-----

Released 2022-05-20

* Fork sqlalchemy-filters https://github.com/juliotrigo/sqlalchemy-filters
  (commit 7222192421c2b235ba1a6cb806ce61fdb165bd79)
* Add some files that git should ignore
* Rename project to sa-filters
* Add support sqlalchemy 1.4 (thanks bodik for his pr to juliotrigo/sqlalchemy-filters),
  and drop support sqlalchemy versions below 1.4. Also drop support python 2
* Add Github Actions and remove Travis CI
* pytest is now supported Python 3.10
* Add copyright to LICENSE
* Add name and email address of the current maintainer
* Add a Github Actions workflow status badge
