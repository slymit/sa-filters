import pytest
from sqlalchemy import func, select, LABEL_STYLE_TABLENAME_PLUS_COL
from sqlalchemy.orm import joinedload
from packaging.version import Version

from sa_filters.exceptions import BadSpec, BadQuery
from sa_filters.models import (
    auto_join, get_default_model, get_query_models, get_model_class_by_name,
    get_model_from_spec
)
from test import SQLALCHEMY_VERSION
from test.models import Base, Bar, Foo, Qux


class TestGetQueryModels(object):

    def test_query_with_no_models(self, session):
        stmt = select()

        entities = get_query_models(stmt)

        assert {} == entities

    def test_query_with_one_model(self, session):
        stmt = select(Bar)

        entities = get_query_models(stmt)

        assert {'Bar': Bar} == entities

    def test_query_with_select_from_model(self, session):
        stmt = select().select_from(Bar)

        entities = get_query_models(stmt)

        assert {'Bar': Bar} == entities

    def test_query_with_select_from_and_join_model(self, session):
        stmt = select().select_from(Bar).join(Foo)

        entities = get_query_models(stmt)

        assert {'Bar': Bar, 'Foo': Foo} == entities

    def test_query_with_multiple_models(self, session):
        stmt = select(Bar, Qux)

        entities = get_query_models(stmt)

        assert {'Bar': Bar, 'Qux': Qux} == entities

    def test_query_with_duplicated_models(self, session):
        stmt = select(Bar, Qux, Bar)

        entities = get_query_models(stmt)

        assert {'Bar': Bar, 'Qux': Qux} == entities

    def test_query_with_one_field(self, session):
        stmt = select(Foo.id)

        entities = get_query_models(stmt)

        assert {'Foo': Foo} == entities

    def test_query_with_multiple_fields(self, session):
        stmt = select(Foo.id, Bar.id, Bar.name)

        entities = get_query_models(stmt)

        assert {'Foo': Foo, 'Bar': Bar} == entities

    def test_query_with_aggregate_func(self, session):
        stmt = select(func.count(Foo.id))

        entities = get_query_models(stmt)

        assert {'Foo': Foo} == entities

    def test_query_with_join(self, session):
        stmt = select(Foo).join(Bar)

        entities = get_query_models(stmt)

        assert {'Foo': Foo, 'Bar': Bar} == entities

    def test_query_with_multiple_joins(self, session):
        stmt = select(Foo).join(Bar).join(Qux, Bar.id == Qux.id)

        entities = get_query_models(stmt)

        assert {'Foo': Foo, 'Bar': Bar, 'Qux': Qux} == entities

    def test_query_with_joinedload(self, session):
        stmt = select(Foo).options(joinedload(Foo.bar))

        entities = get_query_models(stmt)

        # Bar is not added to the query since the joinedload is transparent
        assert {'Foo': Foo} == entities


class TestGetModelFromSpec:

    def test_query_with_no_models(self, session):
        stmt = select()
        spec = {'field': 'name', 'op': '==', 'value': 'name_1'}

        with pytest.raises(BadQuery) as err:
            get_model_from_spec(spec, stmt)

        assert 'The query does not contain any models.' == err.value.args[0]

    def test_query_with_named_model(self, session):
        stmt = select(Bar)
        spec = {'model': 'Bar'}

        model = get_model_from_spec(spec, stmt)
        assert model == Bar

    def test_query_with_missing_named_model(self, session):
        stmt = select(Bar)
        spec = {'model': 'Buz'}

        with pytest.raises(BadSpec) as err:
            get_model_from_spec(spec, stmt)

        assert 'The query does not contain model `Buz`.' == err.value.args[0]

    def test_multiple_models_ambiquous_spec(self, session):
        stmt = select(Bar, Qux)
        spec = {'field': 'name', 'op': '==', 'value': 'name_1'}

        with pytest.raises(BadSpec) as err:
            get_model_from_spec(spec, stmt)

        assert 'Ambiguous spec. Please specify a model.' == err.value.args[0]


class TestGetModelClassByName:

    @pytest.fixture
    def registry(self):
        return Base.registry._class_registry

    def test_exists(self, registry):
        assert get_model_class_by_name(registry, 'Foo') == Foo

    def test_model_does_not_exist(self, registry):
        assert get_model_class_by_name(registry, 'Missing') is None


class TestGetDefaultModel:

    def test_single_model_query(self, session):
        stmt = select(Foo)
        assert get_default_model(stmt) == Foo

    def test_multi_model_query(self, session):
        stmt = select(Foo).join(Bar)
        assert get_default_model(stmt) is None

    def test_empty_query(self, session):
        stmt = select()
        assert get_default_model(stmt) is None


class TestAutoJoin:

    def test_model_not_present(self, session, db_uri):
        stmt = select(Foo).set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL)
        stmt = auto_join(stmt, 'Bar')

        if SQLALCHEMY_VERSION < Version("2.0.0"):
            join_type = "INNER JOIN" if "mysql" in db_uri else "JOIN"

            expected = (
                "SELECT "
                "foo.id AS foo_id, foo.name AS foo_name, "
                "foo.count AS foo_count, foo.bar_id AS foo_bar_id \n"
                "FROM foo {join} bar ON bar.id = foo.bar_id"
                .format(join=join_type)
            )
        else:
            expected = (
                "SELECT "
                "foo.bar_id AS foo_bar_id, foo.id AS foo_id, "
                "foo.name AS foo_name, foo.count AS foo_count \n"
                "FROM foo JOIN bar ON bar.id = foo.bar_id"
            )
        assert str(stmt) == expected

    def test_model_already_present(self, session):
        stmt = select(Foo, Bar).set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL)

        # no join applied
        if SQLALCHEMY_VERSION < Version("2.0.0"):
            expected = (
                "SELECT "
                "foo.id AS foo_id, foo.name AS foo_name, "
                "foo.count AS foo_count, foo.bar_id AS foo_bar_id, "
                "bar.id AS bar_id, bar.name AS bar_name, "
                "bar.count AS bar_count \n"
                "FROM foo, bar"
            )
        else:
            expected = (
                "SELECT "
                "foo.bar_id AS foo_bar_id, foo.id AS foo_id, "
                "foo.name AS foo_name, foo.count AS foo_count, "
                "bar.id AS bar_id, bar.name AS bar_name, "
                "bar.count AS bar_count \n"
                "FROM foo, bar"
            )
        assert str(stmt) == expected

        stmt = auto_join(stmt, 'Bar')
        assert str(stmt) == expected   # no change

    def test_model_already_joined(self, session, db_uri):
        stmt = select(Foo).join(Bar).\
            set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL)

        if SQLALCHEMY_VERSION < Version("2.0.0"):
            join_type = "INNER JOIN" if "mysql" in db_uri else "JOIN"

            expected = (
                "SELECT "
                "foo.id AS foo_id, foo.name AS foo_name, "
                "foo.count AS foo_count, foo.bar_id AS foo_bar_id \n"
                "FROM foo {join} bar ON bar.id = foo.bar_id"
                .format(join=join_type)
            )
        else:
            expected = (
                "SELECT "
                "foo.bar_id AS foo_bar_id, foo.id AS foo_id, "
                "foo.name AS foo_name, foo.count AS foo_count \n"
                "FROM foo JOIN bar ON bar.id = foo.bar_id"
            )
        assert str(stmt) == expected

        stmt = auto_join(stmt, 'Bar')
        assert str(stmt) == expected   # no change

    def test_model_eager_joined(self, session, db_uri):
        stmt = select(Foo).options(joinedload(Foo.bar)).\
            set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL)

        if SQLALCHEMY_VERSION < Version("2.0.0"):
            join_type = "INNER JOIN" if "mysql" in db_uri else "JOIN"

            expected_joined = (
                "SELECT "
                "foo.id AS foo_id, foo.name AS foo_name, "
                "foo.count AS foo_count, foo.bar_id AS foo_bar_id, "
                "bar_1.id AS bar_1_id, bar_1.name AS bar_1_name, "
                "bar_1.count AS bar_1_count \n"
                "FROM foo {join} bar ON bar.id = foo.bar_id "
                "LEFT OUTER JOIN bar AS bar_1 ON bar_1.id = foo.bar_id".format(
                    join=join_type
                )
            )

            expected_eager = (
                "SELECT "
                "foo.id AS foo_id, foo.name AS foo_name, "
                "foo.count AS foo_count, foo.bar_id AS foo_bar_id, "
                "bar_1.id AS bar_1_id, bar_1.name AS bar_1_name, "
                "bar_1.count AS bar_1_count \n"
                "FROM foo "
                "LEFT OUTER JOIN bar AS bar_1 ON bar_1.id = foo.bar_id"
            )
        else:
            expected_joined = (
                "SELECT "
                "foo.bar_id AS foo_bar_id, foo.id AS foo_id, "
                "foo.name AS foo_name, foo.count AS foo_count, "
                "bar_1.id AS bar_1_id, bar_1.name AS bar_1_name, "
                "bar_1.count AS bar_1_count \n"
                "FROM foo JOIN bar ON bar.id = foo.bar_id "
                "LEFT OUTER JOIN bar AS bar_1 ON bar_1.id = foo.bar_id"
            )

            expected_eager = (
                "SELECT "
                "foo.bar_id AS foo_bar_id, foo.id AS foo_id, "
                "foo.name AS foo_name, foo.count AS foo_count, "
                "bar_1.id AS bar_1_id, bar_1.name AS bar_1_name, "
                "bar_1.count AS bar_1_count \n"
                "FROM foo "
                "LEFT OUTER JOIN bar AS bar_1 ON bar_1.id = foo.bar_id"
            )

        assert str(stmt) == expected_eager

        stmt = auto_join(stmt, 'Bar')
        assert str(stmt) == expected_joined

    def test_model_does_not_exist(self, session, db_uri):
        stmt = select(Foo).set_label_style(LABEL_STYLE_TABLENAME_PLUS_COL)

        if SQLALCHEMY_VERSION < Version("2.0.0"):
            expected = (
                "SELECT "
                "foo.id AS foo_id, foo.name AS foo_name, "
                "foo.count AS foo_count, foo.bar_id AS foo_bar_id \n"
                "FROM foo"
            )
        else:
            expected = (
                "SELECT "
                "foo.bar_id AS foo_bar_id, foo.id AS foo_id, "
                "foo.name AS foo_name, foo.count AS foo_count \n"
                "FROM foo"
            )
        assert str(stmt) == expected

        stmt = auto_join(stmt, 'Missing')
        assert str(stmt) == expected   # no change
