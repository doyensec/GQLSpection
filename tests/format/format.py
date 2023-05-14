#!/usr/bin/env python
# coding: utf-8

import sys

from gqlspection.utils.format import PrettyPrinter

with open(sys.argv[1]) as f:
    data = f.read()

pretty = PrettyPrinter()
formatted = pretty.format(data, spaces=2)
print(formatted)
