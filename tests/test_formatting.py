# coding: utf-8
# noinspection PyUnresolvedReferences
from __future__ import unicode_literals

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from gqlspection.utils.format import PrettyPrinter


def pytest_generate_tests(metafunc):
    if 'name' in metafunc.fixturenames:
        pwd = Path(__file__).parent
        names = (x.stem for x in pwd.glob('format/*.graphql'))

        metafunc.parametrize("name", names)


def test_start(name):
    pwd = Path(__file__).parent / 'format'

    # Load expected results (if the file is present)
    path = pwd / "{}.txt".format(name)
    if not path.is_file():
        return
    expected_results = path.read_text()

    # Load the GraphQL query
    path = pwd / "{}.graphql".format(name)

    pretty = PrettyPrinter()
    formatted = pretty.format(path.read_text(), spaces=2)

    print(expected_results)
    print("----")
    print(formatted)
    assert formatted.strip() == expected_results.strip()
