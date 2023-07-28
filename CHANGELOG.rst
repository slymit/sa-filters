Release Notes
=============

Here you can see the full list of changes between sa-filters
versions, where semantic versioning is used: *major.minor.patch*.


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
