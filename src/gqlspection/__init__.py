# coding: utf-8
from __future__ import unicode_literals
from gqlspection.Logger import log

from gqlspection.GQLArg import GQLArg
from gqlspection.GQLEnum import GQLEnum
from gqlspection.GQLField import GQLField
from gqlspection.GQLList import GQLList
from gqlspection.GQLQuery import GQLQuery
from gqlspection.GQLSchema import GQLSchema
from gqlspection.GQLSubQuery import GQLSubQuery
from gqlspection.GQLType import GQLType
from gqlspection.GQLTypeKind import GQLTypeKind
from gqlspection.GQLTypeProxy import GQLTypeProxy
from gqlspection.GQLWrappers import GQLWrapFactory, GQLArgs, GQLEnums, GQLInterfaces, GQLFields, GQLTypes

__all__ = [
    "log",
    "utils",
    "GQLArg",
    "GQLEnum",
    "GQLField",
    "GQLList",
    "GQLQuery",
    "GQLSchema",
    "GQLSubQuery",
    "GQLType",
    "GQLTypeKind",
    "GQLTypeProxy",
    "GQLWrapFactory",
    "GQLArgs",
    "GQLEnums",
    "GQLInterfaces",
    "GQLFields",
    "GQLTypes"
]

# CLI tool entrypoint
from platform import python_implementation
if python_implementation() != 'Jython':
    from gqlspection.cli import cli  # noqa
    __all__.append("cli")
