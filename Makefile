.PHONY: test

POSTGRES_VERSION?=latest
MYSQL_VERSION?=latest


rst-lint:
	rst-lint README.rst
	rst-lint CHANGELOG.rst

flake8:
	flake8 sa_filters test

test: flake8
	pytest test $(ARGS)

coverage: flake8 rst-lint
	coverage run --source sa_filters -m pytest test $(ARGS)
	coverage report --show-missing --fail-under 100


# Docker test containers

mysql-container:
	docker run -d --rm --name mysql-sa-filters -p 3306:3306 \
		-e MYSQL_ALLOW_EMPTY_PASSWORD=yes \
		mysql:$(MYSQL_VERSION)

postgres-container:
	docker run -d --rm --name postgres-sa-filters -p 5432:5432 \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_HOST_AUTH_METHOD=trust \
		-e POSTGRES_DB=test_sa_filters \
		-e POSTGRES_INITDB_ARGS="--encoding=UTF8 --lc-collate=en_US.utf8 --lc-ctype=en_US.utf8" \
		postgres:$(POSTGRES_VERSION)

containers: mysql-container postgres-container