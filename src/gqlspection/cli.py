# coding: utf-8
from __future__ import print_function, unicode_literals
import click
import json
import sys
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
from gqlspection import log, set_log_level, GQLSchema
from gqlspection.points_of_interest.keywords import DEFAULT_CATEGORIES
from gqlspection.six import ensure_text

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
    '-l', '--list', 'list_available', help="Parse GraphQL schema and list queries, mutations or both of them (valid "
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
    '-d', '--depth', default=4, help="Query depth, limits recursion (default: 4)."
)
@click.option(
    '-p', '--poi', is_flag=True, help="Enable 'Points of Interest' reporting."
)
@click.option(
    '-P', '--poi-categories',
    help="A list of enabled PoI categories: " + ','.join(DEFAULT_CATEGORIES)
)
@click.option(
    '--poi-depth', default=2, help="How deep in the schema to look for PoI (default: 2)."
)
@click.option(
    '-k', '--keywords', help="Custom keywords for 'Points of Interest' reporting (comma-separated list)."
)
@click.option(
    '-K', '--keywords-file', help="Custom keywords for 'Points of Interest' reporting (read from a file)."
)
@click.option(
    '-v', '--verbose', is_flag=True, help="Enable verbose logging."
)
@click.option(
    '-g', '--debug', is_flag=True, help="Enable debug logging."
)
def cli(file_=None, url=None, all_queries=False, all_mutations=False, query=None, mutation=None, list_available=None,
        depth=4, poi=False, poi_categories=None, poi_depth=2, keywords=None, keywords_file=None, verbose=False, debug=False):
    """CLI interface for GraphQL schema introspection tool."""

    if verbose:
        set_log_level(log, 'INFO')
    if debug:
        set_log_level(log, 'DEBUG')
    try:
        query = ensure_text(query) if query is not None else None
        mutation = ensure_text(mutation) if mutation is not None else None
        list_available = ensure_text(list_available) if list_available is not None else None

        if keywords:
            keywords = keywords.split(',')

        if poi_categories:
            poi_categories = poi_categories.split(',')

        run(file_, url, all_queries, all_mutations, query, mutation, list_available, depth,
            poi, poi_categories, poi_depth, keywords, keywords_file)
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit()

    sys.exit(0)


def run(file_, url, all_queries, all_mutations, query, mutation, list_available, depth,
        points_of_interest, points_of_interest_categories, poi_depth, keywords, keywords_file):
    if keywords_file:
        with open(keywords_file) as f:
            keywords = [line.strip() for line in f.readlines()]

    schema = parse_schema(file_, url)

    if points_of_interest:
        schema.print_points_of_interest(
            depth=poi_depth,
            categories=points_of_interest_categories,
            keywords=keywords)
        return

    if list_available:
        print_available_stuff(schema, list_available)
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
            if field.name:
                print(schema.generate_query(field, depth).to_string(pad=4))
            else:
                log.debug("field skipped because it does not have name")

    # print mutations
    if schema.mutation and (all_mutations or mutation):
        if all_mutations:
            mutations_to_print = schema.mutation.fields
        else:
            mutations_to_print = (schema.mutation.fields[m] for m in mutation.split(','))

        for field in mutations_to_print:
            if field.name:
                print(schema.generate_mutation(field, depth).to_string(pad=4))
            else:
                log.debug("field skipped because it does not have name")


def parse_schema(file_, url):
    # Parse GraphQL schema
    if file_:
        response = json.loads(Path(file_).read_text())
        return GQLSchema(json=response)
    elif url:
        return GQLSchema(url=url)
    else:
        log.error("Either file or url should be provided.")
        sys.exit(1)


def print_available_stuff(schema, list_available):
    # List stuff if that's what we're asked to do
    if list_available in ('queries', 'all'):
        for query in schema.query.fields:
            # TODO: Would be nice to print a full prototype (with args) here
            print("query %s" % query.name)
    if list_available in ('mutations', 'all') and schema.mutation:
        for mutation in schema.mutation.fields:
            print("mutation %s" % mutation.name)
