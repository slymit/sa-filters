Release Notes
=============

Here you can see the full list of changes between sa-filters
versions, where semantic versioning is used: *major.minor.patch*.


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
