# coding: utf-8
from __future__ import unicode_literals
from builtins import object, str
from gqlspection import log
import gqlspection


class GQLSchema(object):
    types          = None
    query          = None
    mutation       = None

    def __init__(self, url=None, extra_headers=None, json=None, logger=None):
        if logger:
            log.logger = logger

        if json:
            if isinstance(json, str):
                json = self._str_to_json(json)

            if 'data' in json and '__schema' in json['data']:
                original_schema = json['data']['__schema']
            elif '__schema' in json:
                original_schema = json['__schema']
            elif 'types' in json:
                original_schema = json
            else:
                raise Exception("GQLSchema: Couldn't parse JSON schema.")
        elif url:
            introspection_result = self.send_request(url, extra_headers)
            original_schema = introspection_result['data']['__schema']
        else:
            raise Exception("GQLSchema: Provide either JSON or URL.")

        self.types = gqlspection.GQLTypes(self, original_schema)

        self.query    = self._extract_query_type(original_schema)
        self.mutation = self._extract_mutation_type(original_schema)

    @staticmethod
    def _str_to_json(data):
        import json
        return json.loads(data)

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
        if 'mutationType' in schema:
            name = schema['mutationType'].get('name', None)
            if name:
                return gqlspection.GQLTypeProxy(name, self)
            else:
                raise None
        else:
            return None

    @staticmethod
    def send_request(url, extra_headers=None, minimize=True):
        import requests
        from gqlspection.introspection_query import get_introspection_query

        headers = {'Content-Type': 'application/json'}
        if extra_headers:
            headers.update(extra_headers)

        result = requests.post(url, json={'query': get_introspection_query(minimize=minimize)}, headers=headers).json()
        if 'errors' in result:
            raise Exception([error['message'] for error in result['errors']])

        return result

    def generate_query(self, name):
        if isinstance(name, str):
            field = self.query.fields[name]
        else:
            field = name
        return gqlspection.GQLQuery(self.query, 'query', fields=[field])

    def generate_mutation(self, name):
        if isinstance(name, str):
            field = self.query.fields[name]
        else:
            field = name
        return gqlspection.GQLQuery(self.mutation, 'mutation', fields=[field])
