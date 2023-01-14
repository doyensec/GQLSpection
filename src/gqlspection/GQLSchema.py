import gqlspection


class GQLSchema(object):
    types          = None  # type: gqlspection.GQLTypes
    query          = None  # type: gqlspection.GQLType
    mutation       = None  # type: gqlspection.GQLType
    _query_type    = None  # type: str
    _mutation_type = None  # type: str

    def __init__(self, url, extra_headers=None):
        introspection_result = self.send_request(url, extra_headers)
        original_schema = introspection_result['data']['__schema']

        self._query_type    = original_schema['queryType']['name']
        self._mutation_type = original_schema['mutationType']['name']

        self.types = gqlspection.GQLTypes(self, original_schema)

        self.query          = self.types[self._query_type]
        self.mutation       = self.types[self._mutation_type]

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
        if type(name) == str:
            field = self.query.fields[name]
        else:
            field = name
        return gqlspection.GQLQuery(self.query, 'query', fields=[field])

    def generate_mutation(self, name):
        if type(name) == str:
            field = self.query.fields[name]
        else:
            field = name
        return gqlspection.GQLQuery(self.mutation, 'mutation', fields=[field])

    def print_sample_queries(self):
        for field in self.query.fields:
            query = gqlspection.GQLQuery(self.query, 'query', fields=[field])

            print("Query '%s.graphql':" % field.name)
            query_string = self.generate_query(field)\
                .print_query()\
                .splitlines()
            print('\n'.join('    ' + line for line in query_string))
            print("")
