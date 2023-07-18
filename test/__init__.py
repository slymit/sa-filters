# -*- coding: utf-8 -*-
from packaging.version import parse
from sqlalchemy import __version__

SQLALCHEMY_VERSION = parse(__version__)


def error_value(exception):
    return exception.value.args[0]
