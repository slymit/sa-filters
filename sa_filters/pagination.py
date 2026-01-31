# -*- coding: utf-8 -*-
import math
from collections import namedtuple
from typing import Optional, Union

from sqlalchemy.sql import Select
from sqlalchemy.orm import Query

from .exceptions import InvalidPage


Pagination = namedtuple(
    'Pagination', ['page_number', 'page_size', 'num_pages', 'total_results']
)


def apply_pagination(
        stmt: Union[Select, Query],
        page_number: Optional[int] = None,
        page_size: Optional[int] = None,
        total_results: int = 0
) -> tuple[Union[Select, Query], Pagination]:
    """Apply pagination to a SQLAlchemy :class:`sqlalchemy.sql.Select` object
    or a :class:`sqlalchemy.orm.Query` object.

    :param stmt:
        The statement to be processed.

    :param page_number:
        Page to be returned (starts and defaults to 1).

    :param page_size:
        Maximum number of results to be returned in the page (defaults
        to the total results).

    :param total_results:
        Total results (defaults to 0).

    :returns:
        A 2-tuple with the paginated SQLAlchemy :class:`sqlalchemy.sql.Select`
        instance or :class:`sqlalchemy.orm.Query` instance and
        a pagination namedtuple.

        The pagination object contains information about the results
        and pages: ``page_size`` (defaults to ``total_results``),
        ``page_number`` (defaults to 1), ``num_pages`` and
        ``total_results``.

    Basic usage::

        >>> stmt, pagination = apply_pagination(stmt, 1, 10, 22)
        >>> result = session.execute(stmt).all()
        >>> len(result)
        10
        >>> pagination.page_size
        10
        >>> pagination.page_number
        1
        >>> pagination.num_pages
        3
        >>> pagination.total_results
        22
        >>> page_number, page_size, num_pages, total_results = pagination
    """
    stmt = _limit(stmt, page_size)

    # Page size defaults to total results
    if page_size is None or (page_size > total_results > 0):
        page_size = total_results

    stmt = _offset(stmt, page_number, page_size)

    # Page number defaults to 1
    if page_number is None:
        page_number = 1

    num_pages = _calculate_num_pages(page_number, page_size, total_results)

    return stmt, Pagination(page_number, page_size, num_pages, total_results)


def _limit(stmt, page_size):
    if page_size is not None:
        if page_size < 0:
            raise InvalidPage(
                'Page size should not be negative: {}'.format(page_size)
            )

        stmt = stmt.limit(page_size)

    return stmt


def _offset(stmt, page_number, page_size):
    if page_number is not None:
        if page_number < 1:
            raise InvalidPage(
                'Page number should be positive: {}'.format(page_number)
            )

        stmt = stmt.offset((page_number - 1) * page_size)

    return stmt


def _calculate_num_pages(page_number, page_size, total_results):
    if page_size == 0:
        return 0

    return math.ceil(float(total_results) / float(page_size))
