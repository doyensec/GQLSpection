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
        names = (x.stem for x in pwd.glob('poi/*.json'))

        metafunc.parametrize("name", names)


def test_start(name):
    pwd = Path(__file__).parent / 'poi'

    # Load expected results (if the file is present)
    path = pwd / "{}.txt".format(name)
    if not path.is_file():
        return
    expected_results = path.read_text()

    # Load the GraphQL schema
    path = pwd / "{}.json".format(name)
    schema = GQLSchema(json=path.read_text())

    # generate a string representing queries / mutations
    result = schema._print_points_of_interest()

    print(type(result), type(expected_results))
    assert result.strip() == expected_results.strip()
