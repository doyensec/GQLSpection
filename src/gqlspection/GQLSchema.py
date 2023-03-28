# coding: utf-8
from __future__ import unicode_literals
import json as j
from gqlspection.six import text_type, ensure_text
from gqlspection import log
import gqlspection


class GQLSchema(object):
    types          = None
    query          = None
    mutation       = None

    def __init__(self, url=None, extra_headers=None, json=None):
        # type: (Optional[str], Optional[dict], Optional[str | dict]) -> None
        log.debug("GQLSchema initialized.")
        if json:
            if type(json) == text_type:
                json = j.loads(json)
            elif type(json) != dict:
                raise Exception("GQLSchema: Couldn't parse provided JSON, it's not a string and not a dictionary.")

            if 'data' in json and '__schema' in json['data']:
                original_schema = json['data']['__schema']
            elif '__schema' in json:
                original_schema = json['__schema']
            elif 'types' in json:
                original_schema = json
            else:
                raise Exception("GQLSchema: Couldn't parse JSON schema.")
        elif url:
            url = ensure_text(url)
            introspection_result = self.send_request(url, extra_headers)
            original_schema = introspection_result['data']['__schema']
        else:
            raise Exception("GQLSchema: Provide either JSON or URL.")

        self.types = gqlspection.GQLTypes(self, original_schema)

        self.query    = self._extract_query_type(original_schema)
        self.mutation = self._extract_mutation_type(original_schema)

    def _extract_query_type(self, schema):
        """Get the query type name (typically 'Query').

        According to GraphQL specs, this should always be present. We could easily fall back to 'Query' though, file
        a bug report if there is a real-world need for that.

            __schema {
                queryType {
                    name
                }
            }
        """
        if 'queryType' in schema:
            name = schema['queryType'].get('name', False)
            if name:
                return gqlspection.GQLTypeProxy(name, self)
            else:
                raise Exception("GQLSchema: Invalid schema - queryType is null. File a bug if this happens in real "
                                "world.")
        else:
            raise Exception("GQLSchema: Invalid schema - no queryType (absence of queryType is not allowed according "
                            "to GraphQL spec, file a bug report if this happens in real world).")

    def _extract_mutation_type(self, schema):
        """Get the mutation type and return None if it has not been defined.

            __schema {
                mutationType {
                    name
                }
            }
        """
        # According to GraphQL spec mutationType should always be present, but some tools like
        # https://github.com/nikitastupin/clairvoyance omit it anyway.
        if 'mutationType' in schema and schema['mutationType']:
            name = schema['mutationType'].get('name', None)
            if name:
                return gqlspection.GQLTypeProxy(name, self)
            else:
                log.warning("Couldn't find mutationType. This isn't allowed by the spec, but I'll let it slide.")
                return None
        else:
            return None

    @staticmethod
    def send_request(url, extra_headers=None, minimize=True):
        import requests
        from gqlspection.introspection_query import get_introspection_query

        headers = {'Content-Type': 'application/json'}
        if extra_headers:
            for k, v in extra_headers:
                k, v = ensure_text(k), ensure_text(v)
                headers[k] = v

        result = requests.post(url, json={'query': get_introspection_query(minimize=minimize)}, headers=headers).json()
        if 'errors' in result:
            raise Exception([error['message'] for error in result['errors']])

        return result

    def generate_query(self, name, depth=4):
        if type(name) == text_type:
            field = self.query.fields[name]
        else:
            field = name
        return gqlspection.GQLQuery(self.query, 'query', fields=[field], depth=depth)

    def generate_mutation(self, name, depth=4):
        if type(name) == text_type:
            field = self.query.fields[name]
        else:
            field = name
        return gqlspection.GQLQuery(self.mutation, 'mutation', fields=[field], depth=depth)

    @property
    def queries(self):
        return (
            gqlspection.GQLQuery(self.query, 'query', name=field.name, fields=[field])
            for field in self.query.fields if field.name
        )

    @property
    def mutations(self):
        if not self.mutation:
            return ()
        return (
            gqlspection.GQLQuery(self.mutation, 'mutation', name=field.name, fields=[field])
            for field in self.mutation.fields if field.name
        )
