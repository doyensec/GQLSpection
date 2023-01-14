import gqlspection
from utils import safe_get_list


class GQLWrapFactory(object):
    schema = None  # type: gqlspection.GQLSchema
    json   = None  # type: dict

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
        return (gqlspection.GQLType.from_json(t, schema) for t in safe_get_list(json, 'types'))


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
