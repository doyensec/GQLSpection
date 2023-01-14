# GQLSpection

Python 2.7 compatible library for parsing GraphQL introspection query and automatic query generation.

```python
>>> from gqlspection import GQLSchema
>>> schema = GQLSchema('https://swapi-graphql.netlify.app/.netlify/functions/index')
>>> # Print a single query
>>> query = schema.generate_query('allFilms')
>>> print(query.print_query())
>>> # Print all possible queries
>>> schema.print_sample_queries()
```

## Installation

gqlspection should be available (soon) on PyPI:

```bash
$ pip install gqlspection
```
