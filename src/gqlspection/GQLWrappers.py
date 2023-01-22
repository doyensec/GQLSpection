# coding: utf-8
from __future__ import absolute_import, unicode_literals
from builtins import object
from gqlspection import log
import gqlspection
from .utils import safe_get_list


class GQLWrapFactory(object):
    schema = None
    json   = None

    def __init__(self, schema, json):
        self.schema = schema
        self.json = json

    def fields(self):
        return GQLFields(self.schema, self.json)

    def interfaces(self):
        return GQLInterfaces(self.schema, self.json)

    def enums(self):
        return GQLEnums(self.schema, self.json)

    def args(self):
        return GQLArgs(self.schema, self.json)


class GQLWrapper(gqlspection.GQLList):
    # This should be overwritten through inheritance
    @staticmethod
    def _extract_elements(schema, json):
        return ()

    def __init__(self, schema, json):
        elements = (
            element for element in self._extract_elements(schema, json)
            if not element.name.startswith('__')
        )

        super(GQLWrapper, self).__init__(elements)


class GQLTypes(GQLWrapper):
    def _extract_elements(self, schema, json):
        elements = []
        scalars = set()
        for t in safe_get_list(json, 'types'):
            el = gqlspection.GQLType.from_json(t, schema)
            log.info("Adding new type definition: %s", el.name)
            elements.append(el)

            if el.kind.kind == 'SCALAR':
                scalars.add(el.kind.name)

        # populate standard types if not present in supplied schema
        for scalar in gqlspection.GQLTypeKind.builtin_scalars:
            log.info("Adding missing default scalar: %s" % scalar)
            if scalar not in scalars:
                elements.append(gqlspection.GQLType(
                    name = scalar,
                    kind = gqlspection.GQLTypeKind(
                        name=scalar,
                        kind='SCALAR'
                    ),
                    description="Built-in scalar type.",
                    schema=schema
                ))

        return elements


class GQLFields(GQLWrapper):
    @staticmethod
    def _extract_elements(schema, json):
        return (gqlspection.GQLField.from_json(field, schema) for field in safe_get_list(json, 'fields'))


class GQLInterfaces(GQLWrapper):
    """Iterator-like wrapper around 'interfaces' type attribute which lists interfaces that object implements.

    An example of a valid field:

          "interfaces": [
            {
              "kind": "INTERFACE",
              "name": "Error",
              "ofType": null
            }
          ],
    """
    @staticmethod
    def _extract_elements(schema, json):
        return (gqlspection.GQLTypeProxy(interface['name'], schema) for interface in safe_get_list(json, 'interfaces'))


class GQLEnums(GQLWrapper):
    @staticmethod
    def _extract_elements(schema, json):
        return (gqlspection.GQLEnum.from_json(enum) for enum in safe_get_list(json, 'enumValues'))


class GQLArgs(GQLWrapper):
    @staticmethod
    def _extract_elements(schema, json):
        return (gqlspection.GQLArg.from_json(arg, schema) for arg in safe_get_list(json, 'inputFields'))
