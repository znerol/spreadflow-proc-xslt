from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import collections

from twisted.internet import defer

# Use parser from defusedxml.
from defusedxml.lxml import fromstring as defusedxml_fromstring

# XSLT is not present in defusedxml, explicitely get the one from lxml.
from lxml import etree

class XSLT(object):

    def __init__(self, path, key='content', destkey=None, encoding=None, params=None, strparams=None, paramskey=None, strparamskey=None, coiterate=True):
        self.path = path
        self.key = key
        self.destkey = destkey if destkey else key
        self.doc = None
        self.transformer = None
        self.encoding = encoding

        self._literal_params = {}
        if params:
            self._literal_params.update(params)

        if strparams:
            for param, value in strparams.items():
                self._literal_params[param] = etree.XSLT.strparam(value)

        self.paramskey = paramskey
        self.strparamskey = strparamskey

        if coiterate is True:
            from twisted.internet.task import coiterate

        if coiterate:
            self.coiterate = coiterate
        else:
            self.coiterate = self._dummy_coiterate

    @defer.inlineCallbacks
    def __call__(self, item, send):
        yield self.coiterate(self._transform(item))
        send(item, self)

    def _transform(self, item):
        if not self.doc:
            self.doc = etree.parse(self.path)
            yield

        if not self.transformer:
            self.transformer = etree.XSLT(self.doc)

        for oid in item['inserts']:
            if self.key:
                markup = item['data'][oid][self.key]
                doc = defusedxml_fromstring(markup)
            else:
                doc = self.doc

            params = self._extract_params(item['data'][oid])
            markup = bytes(self.transformer(doc, **params))

            if self.encoding is not None:
                markup = markup.decode(self.encoding)

            item['data'][oid][self.destkey] = markup

            yield

    def _dummy_coiterate(self, iterator):
        for x in iterator:
            continue

        return defer.succeed(iterator)

    def _extract_params(self, doc):
        result = self._literal_params.copy()

        if self.paramskey:
            result.update(doc[self.paramskey])

        if self.strparamskey:
            for param, value in doc[self.strparamskey].items():
                result[param] = etree.XSLT.strparam(value)

        return result
