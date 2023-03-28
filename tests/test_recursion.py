# coding: utf-8
# noinspection PyUnresolvedReferences
from __future__ import unicode_literals

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from gqlspection import GQLSchema


def pytest_generate_tests(metafunc):
    if 'name' in metafunc.fixturenames:
        pwd = Path(__file__).parent
        names = (x.stem for x in pwd.glob('recursion/*.json'))

        metafunc.parametrize("name", names)
        metafunc.parametrize("mode", (1, 2))


def test_start(name, mode):
    pwd = Path(__file__).parent / 'recursion'

    # Load expected results (if the file is present)
    path = pwd / "{}.{}.txt".format(name, mode)
    if not path.is_file():
        return
    expected_results = path.read_text()

    # Load the GraphQL schema
    path = pwd / "{}.json".format(name)
    schema = GQLSchema(json=path.read_text())

    # generate a string representing queries / mutations
    result = '\n'.join(schema.generate_query(field, depth=mode).to_string() for field in schema.query.fields)

    print(type(result), type(expected_results))
    assert result.strip() == expected_results.strip()
