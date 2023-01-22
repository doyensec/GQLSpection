# coding: utf-8
from __future__ import unicode_literals
from builtins import object
from gqlspection import log
import gqlspection


class GQLTypeProxy(object):
    name = ''
    schema = None
    _upstream = None
    max_depth = 4

    def __init__(self, name, schema):
        self.name = name
        self.schema = schema

    @property
    def upstream(self):
        # use cached value if present
        if self._upstream:
            return self._upstream

        if self.name in self.schema.types:
            self._upstream = self.schema.types[self.name]
            return self._upstream
        else:
            if log.is_debug:
                import pdb
                pdb.set_trace()
                log.debug("Found an unknown type: '%s'. At this time following types are present in schema:", self.name)
                for t in self.schema.types:
                    log.debug("    %s(%s) [%s]" % (type(t.name), t.name, t.kind.kind))

            raise Exception("GQLTypeProxy: type '%s' not defined" % self.name)

    def _proxy_getattr(self, item, levels):
        if levels >= self.max_depth:
            raise Exception("GQLTypeProxy: reached the recursion limit!")
        return getattr(self, item)

    def __getattr__(self, item):
        proxy = getattr(self.upstream, '_proxy_getattr', None)
        if proxy:
            # nested object detected, pass execution to proxy
            return proxy(item, 0)

        return getattr(self.upstream, item)

    def __dir__(self):
        return super(gqlspection.GQLType, self.upstream).__dir__()
