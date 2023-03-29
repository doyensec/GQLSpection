# coding: utf-8
from gqlspection.utils import pretty_print_graphql

simple = """
query a {
  b
  c
  d(e: f, g: h) {
    i
    j
    k(l: m, n: o) {
      p
    }
    q
    r
  }
  s
  t
}
"""


def test_pretty_print():
    result = pretty_print_graphql(simple)
    print(result)
    assert result.strip() == simple.strip()
