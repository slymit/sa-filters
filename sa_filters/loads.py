from typing import Any, Dict, List, Union

from sqlalchemy.sql import Select
from sqlalchemy.orm import Load, Query

from .exceptions import BadLoadFormat
from .models import Field, auto_join, get_model_from_spec, get_default_model


class LoadOnly(object):

    def __init__(self, load_spec):
        self.load_spec = load_spec

        try:
            field_names = load_spec['fields']
        except KeyError:
            raise BadLoadFormat('`fields` is a mandatory attribute.')
        except TypeError:
            raise BadLoadFormat(
                'Load spec `{}` should be a dictionary.'.format(load_spec)
            )

        self.field_names = field_names

    def get_named_models(self):
        if "model" in self.load_spec:
            return {self.load_spec['model']}
        return set()

    def format_for_sqlalchemy(self, query, default_model):
        load_spec = self.load_spec
        field_names = self.field_names

        model = get_model_from_spec(load_spec, query, default_model)
        fields = [Field(model, field_name) for field_name in field_names]

        return Load(model).load_only(
            *[field.get_sqlalchemy_field() for field in fields]
        )


def get_named_models(loads):
    models = set()
    for load in loads:
        models.update(load.get_named_models())
    return models


def apply_loads(
        stmt: Union[Select, Query],
        load_spec: Union[List[Dict[str, Any]], Dict[str, Any], List[str]]
) -> Union[Select, Query]:
    """Apply load restrictions to a :class:`sqlalchemy.sql.Select` object
    or a :class:`sqlalchemy.orm.Query` object.

    :param stmt:
        The statement to be processed.

    :param load_spec:
        A list of dictionaries, where each item contains the fields to load
        for each model.

        Example::

            load_spec = [
                {'model': 'Foo', fields': ['id', 'name']},
                {'model': 'Bar', 'fields': ['name']},
            ]

        If the query being modified refers to a single model, the `model` key
        may be omitted from the load spec. The following shorthand form is
        also accepted when the model can be inferred::

            load_spec = ['id', 'name']

    :returns:
        The :class:`sqlalchemy.sql.Select` object or
        a :class:`sqlalchemy.orm.Query` object
        after the load restrictions have been applied.
    """
    if (
        isinstance(load_spec, list) and
        all(map(lambda item: isinstance(item, str), load_spec))
    ):
        load_spec = {'fields': load_spec}

    if isinstance(load_spec, dict):
        load_spec = [load_spec]

    loads = [LoadOnly(item) for item in load_spec]

    default_model = get_default_model(stmt)

    load_models = get_named_models(loads)
    stmt = auto_join(stmt, *load_models)

    sqlalchemy_loads = [
        load.format_for_sqlalchemy(stmt, default_model) for load in loads
    ]
    if sqlalchemy_loads:
        stmt = stmt.options(*sqlalchemy_loads)

    return stmt
