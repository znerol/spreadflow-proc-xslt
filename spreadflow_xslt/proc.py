from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import collections
import functools

from twisted.internet import defer

# Use parser from defusedxml.
from defusedxml.lxml import fromstring as defusedxml_fromstring

# XSLT is not present in defusedxml, explicitely get the one from lxml.
from lxml import etree

class XSLT(object):

    def __init__(self, path, key='content', destkey=None, encoding=None, params=None, coiterate=True):
        self.path = path
        self.key = key
        self.destkey = destkey if destkey else key
        self.doc = None
        self.transformer = None
        self.encoding = encoding

        if coiterate == True:
            from twisted.internet.task import coiterate

        if coiterate:
            self.coiterate = coiterate
        else:
            self.coiterate = self._dummy_coiterate

        self._literal_params = ()
        self._strparams = ()
        self._rawparams = ()

        try:
            strtype = basestring
        except NameError:
            strtype = str

        def _add_literal_param(param, value, raw=False):
            self._literal_params += ((param, value),) if raw else ((param, etree.XSLT.strparam(value)),)

        if params:
            for param, value in params.items():
                if isinstance(value, collections.Mapping):
                    raw = value.get('raw', False)
                    if 'value' in value:
                        _add_literal_param(param, value['value'], raw)
                        continue

                    if 'from' in value:
                        if raw:
                            self._rawparams += ((param, value['from']),)
                        else:
                            self._strparams += ((param, value['from']),)
                        continue

                if isinstance(value, strtype):
                    _add_literal_param(param, value, False)
                    continue

                _add_literal_param(param, value, True)

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

            if self.encoding != None:
                markup = markup.decode(self.encoding)

            item['data'][oid][self.destkey] = markup

            yield

    def _dummy_coiterate(self, iterator):
        for x in iterator:
            continue

        return defer.succeed(iterator)

    def _extract_params(self, doc):
        return dict(
            self._literal_params +
            tuple([(param, doc[value]) for param, value in self._rawparams]) +
            tuple([(param, etree.XSLT.strparam(doc[value])) for param, value in self._strparams])
        )
