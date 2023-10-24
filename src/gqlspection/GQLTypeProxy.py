# coding: utf-8
from __future__ import unicode_literals
from gqlspection import log
from gqlspection.six import ensure_text

class GQLTypeProxy(object):
    """A proxy for GQLType that allows for lazy loading of nested objects."""
    def __init__(self, name, schema):
        # type: (str, GQLSchema) -> None
        self.name = ensure_text(name)
        self.schema = schema
        self.upstream = None

    def __getattr__(self, item):
        # Once the attribute is accessed, we load the actual object from the schema and replace attribute with strong reference
        upstream = self.upstream
        if upstream is None:
            try:
                upstream = self.schema.types[self.name]
                self.upstream = upstream
            except KeyError:
                raise AttributeError("GQLTypeProxy: type '%s' not defined" % self.name)
        upstream_item = getattr(upstream, item)

        setattr(self, item, upstream_item)  # Setting attribute to the proxy
        return upstream_item
