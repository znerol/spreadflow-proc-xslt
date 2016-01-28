from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import collections
import glob
import os

from twisted.internet import defer

# Use parser from defusedxml if possible.
from defusedxml import lxml as etree

# XSLT is not present in defusedxml, explicitely get the one from lxml.
from lxml.etree import XSLT

class XsltPipeline(object):

    extensions = ('xsl', 'xslt')

    def __init__(self, path, attrib='content', dest='transformed', encoding=None, params=None, coiterate=True):
        self.path = path
        self.attrib = attrib
        self.dest = dest
        self.transformers = []
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

        def _add_literal_param(key, value, raw=False):
            self._literal_params += ((key, value),) if raw else ((key, XSLT.strparam(value)),)

        if params:
            for key, value in params.items():
                if isinstance(value, collections.Mapping):
                    raw = value.get('raw', False)
                    if 'value' in value:
                        _add_literal_param(key, value['value'], raw)
                        continue

                    if 'from' in value:
                        if raw:
                            self._rawparams += ((key, value['from']),)
                        else:
                            self._strparams += ((key, value['from']),)
                        continue

                if isinstance(value, basestring):
                    _add_literal_param(key, value, False)
                    continue

                _add_literal_param(key, value, True)


    def start(self):
        if (os.path.isdir(self.path)):
            patterns = [os.path.join(self.path, '*.%s' % ext) for ext in self.extensions]
            discovered = reduce(lambda head, tail: head + tail, [glob.glob(pattern) for pattern in patterns], [])
            for path in sorted(discovered, key=lambda s: s.lower()):
                self._load_file(path)
        else:
            self._load_file(self.path)

    @defer.inlineCallbacks
    def __call__(self, item, send):
        yield self.coiterate(self._transform(item))
        send(item, self)

    def _transform(self, item):
        for oid in item['inserts']:
            markup = item['data'][oid][self.attrib]
            for t in self.transformers:
                params = self._extract_params(item['data'][oid])
                doc = etree.fromstring(markup)
                markup = bytes(t(doc, **params))
                yield

            if self.encoding != None:
                markup = markup.decode(self.encoding)

            item['data'][oid][self.dest] = markup

    def _dummy_coiterate(self, iterator):
        for x in iterator:
            continue

        return defer.succeed(iterator)

    def _load_file(self, path):
        self.transformers.append(XSLT(etree.parse(path)))

    def _extract_params(self, doc):
        return dict(
            self._literal_params +
            tuple([(key, doc[value]) for key, value in self._rawparams]) +
            tuple([(key, XSLT.strparam(doc[value])) for key, value in self._strparams])
        )
