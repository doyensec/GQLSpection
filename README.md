# GQLSpection

CLI tool and Python 2.7+ compatible library for parsing GraphQL introspection query and automatic query generation.

![License](https://img.shields.io/github/license/doyensec/gqlspection?style=for-the-badge)
![Python Versions](https://img.shields.io/pypi/pyversions/gqlspection?style=for-the-badge)
![Jython Version](https://img.shields.io/badge/Jython%20%28lib%20only%29-2.7.3-success?style=for-the-badge)


![Status](https://img.shields.io/github/actions/workflow/status/doyensec/gqlspection/QA.yml?style=for-the-badge)
![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/doyensec/GQLSpection/python-coverage-comment-action-data/endpoint.json&style=for-the-badge)

## Installation

GQLSpection is available on PyPI (Python 2.7 and Python 3+ versions are supported).

Regular installation:

```bash
$ pip install gqlspection[cli]
```

Installation with development dependencies from git repo:

```bash
$ git clone https://github.com/doyensec/GQLSpection.git
$ cd GQLSpection
$ virtualenv venv
$ . ./venv/bin/activate
$ pip install -e ".[dev]"
$ # Only needed in ZSH to locate newly added binaries:
$ rehash
$ pre-commit install
```

## Usage of the CLI tool

Load schema from file and print all query and mutation names in the schema:

```bash
$ gqlspection -f schema.json -l all
```

Send introspection query and generate queries & mutations for everything:

```bash
$ gqlspection -u https://.../graphql
```

Generate a single query:

```bash
$ gqlspection -u https://.../graphql -q something
```

Generate a number of mutations:

```bash
$ gqlspection -f schema.json -m one,two,three
```

### Full help

```
$ ./gqlspection -h
Usage: gqlspection [OPTIONS]

Options:
  -f, --file TEXT      File with the GraphQL schema (introspection JSON).
  -u, --url TEXT       URL of the GraphQL endpoint with enabled introspection.

  -l, --list TEXT      Parse GraphQL schema and list queries, mutations or
                       both of them (valid values are: 'queries', 'mutations'
                       or 'all').

  -q, --query TEXT     Only print named queries (argument is a comma-separated
                       list of query names).

  -m, --mutation TEXT  Only print named mutations (argument is a comma-
                       separated list of mutation names).

  -Q, --all-queries    Only print queries (by default both queries and
                       mutations are printed).

  -M, --all-mutations  Only print mutations (by default both queries and
                       mutations are printed).

  -h, --help           Show this message and exit.
```

## Usage of the Python library

Import the library:

```python
>>> from gqlspection import GQLSchema
```

Send introspection query and print a single query:

```python
>>> schema = GQLSchema(url='https://.../graphql')
>>> query = schema.generate_query('SOME_TYPE')
>>> print(query.str)
```

Parse introspection schema from a JSON file and print all mutations:

```python
>>> from pathlib import Path
>>> import json
>>> data = json.loads(Path(FILE_NAME).read_text())
>>> schema = GQLSchema(json=data)
>>> for field in schema.mutation.fields:
>>>     print(schema.generate_mutation(field).str())
```
