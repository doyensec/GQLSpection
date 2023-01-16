# noinspection PyUnresolvedReferences
import pytest

from pathlib2 import Path
from gqlspection import GQLSchema


def pytest_generate_tests(metafunc):
    if 'name' in metafunc.fixturenames:
        pwd = Path(__file__).parent
        names = (x.stem for x in pwd.glob('data/*.json'))
        metafunc.parametrize("name", names)
        metafunc.parametrize("mode", ('queries', 'mutations'))


def test_start(name, mode):
    pwd = Path(__file__).parent / 'data'

    # Load expected results (if the file is present)
    path = pwd / "{}.{}.txt".format(name, mode)
    if not path.is_file():
        return
    expected_results = path.read_text()

    # Load the GraphQL schema
    path = pwd / "{}.json".format(name)
    schema = GQLSchema(json=path.read_text())

    # generate a string representing queries / mutations
    if mode == 'queries':
        result = '\n'.join(schema.generate_query(field).str() for field in schema.query.fields)
    else:
        result = '\n'.join(schema.generate_mutation(field).str() for field in schema.mutation.fields)

    assert result == expected_results
