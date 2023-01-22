# coding: utf-8
from __future__ import print_function, unicode_literals
import click
import json
import sys
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
from gqlspection import log, GQLSchema

click.disable_unicode_literals_warning = True

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '-f', '--file', 'file_', help="File with the GraphQL schema (introspection JSON)."
)
@click.option(
    '-u', '--url', help="URL of the GraphQL endpoint with enabled introspection."
)
@click.option(
    '-l', '--list', 'stuff_to_print', help="Parse GraphQL schema and list queries, mutations or both of them (valid "
                                           "values are: 'queries', 'mutations' or 'all')."
)
@click.option(
    '-q', '--query', help="Only print named queries (argument is a comma-separated list of query names)."
)
@click.option(
    '-m', '--mutation', help="Only print named mutations (argument is a comma-separated list of mutation names)."
)
@click.option(
    '-Q', '--all-queries', is_flag=True, help="Only print queries (by default both queries and mutations are printed)."
)
@click.option(
    '-M', '--all-mutations', is_flag=True, help="Only print mutations (by default both queries and mutations are "
                                                "printed)."
)
@click.option(
    '-v', '--verbose', is_flag=True, help="Enable verbose logging."
)
def cli(file_=None, url=None, all_queries=False, all_mutations=False, query=None, mutation=None, stuff_to_print=None,
        verbose=False):
    if verbose:
        import logging
        log.logger.setLevel(logging.DEBUG)
    try:
        run(file_, url, all_queries, all_mutations, query, mutation, stuff_to_print)
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit()

    sys.exit(0)


def run(file_, url, all_queries, all_mutations, query, mutation, stuff_to_print):
    schema = parse_schema(file_, url)

    if stuff_to_print:
        print_available_stuff(schema, stuff_to_print)
        return

    # if explicit queries (-q) or mutations (-m) provided, they take priority
    if query or mutation:
        all_queries = all_mutations = False
    # otherwise print all queries and mutations, unless one of the -Q / -M flags is specified
    elif not all_queries and not all_mutations:
        all_queries = all_mutations = True

    # print queries
    if all_queries or query:
        if all_queries:
            queries_to_print = schema.query.fields
        else:
            queries_to_print = (schema.query.fields[q] for q in query.split(','))

        for field in queries_to_print:
            print(schema.generate_query(field).str(pad=4))

    # print mutations
    if schema.mutation and (all_mutations or mutation):
        if all_mutations:
            mutations_to_print = schema.mutation.fields
        else:
            mutations_to_print = (schema.mutation.fields[m] for m in mutation.split(','))

        for field in mutations_to_print:
            print(schema.generate_mutation(field).str(pad=4))


def parse_schema(file_, url):
    # Parse GraphQL schema
    if file_:
        response = json.loads(Path(file_).read_text())
        return GQLSchema(json=response)
    elif url:
        return GQLSchema(url=url)
    else:
        log.err("Either file or url should be provided.")
        sys.exit(1)


def print_available_stuff(schema, stuff_to_print):
    # List stuff if that's what we're asked to do
    if stuff_to_print in ('queries', 'all'):
        for query in schema.query.fields:
            # TODO: Would be nice to print a full prototype (with args) here
            print("query %s" % query.name)
    if stuff_to_print in ('mutations', 'all') and schema.mutation:
        for mutation in schema.mutation.fields:
            print("mutation %s" % mutation.name)
