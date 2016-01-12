from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import collections
import glob
import os

from twisted.internet import defer
from twisted.internet.task import coiterate

# Use parser from defusedxml if possible.
from defusedxml import lxml as etree

# XSLT is not present in defusedxml, explicitely get the one from lxml.
from lxml.etree import XSLT

class XsltPipeline(object):

    extensions = ('xsl', 'xslt')

    def __init__(self, path, attrib='content', dest='transformed', params=None):
        self.path = path
        self.attrib = attrib
        self.dest = dest
        self.transformers = []

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
            for path in sorted(reduce(lambda x, y: x + y, [glob.glob(pattern) for pattern in patterns], [])):
                self._load_file(path)
        else:
            self._load_file(self.path)

    @defer.inlineCallbacks
    def __call__(self, item, send):
        yield coiterate(self._transform(item))
        send(item, self)

    def _transform(self, item):
        for oid in item['inserts']:
            markup = item['data'][oid][self.attrib]
            # work around lxml insisting on untagged strings.
            # TODO: This is brittle. Either exclusively work with unicode
            # throughout the system (and thus remove the XML declaration when
            # reading a file from disk) or exclusively work with buffers (and
            # always keep the XML declaration).
            if isinstance(markup, unicode):
                markup = markup.encode("utf-8")
            for t in self.transformers:
                params = self._extract_params(item['data'][oid])
                doc = etree.fromstring(markup)
                markup = unicode(t(doc, **params))
                yield

            item['data'][oid][self.dest] = markup


    def _load_file(self, path):
        self.transformers.append(XSLT(etree.parse(path)))

    def _extract_params(self, doc):
        return dict(
            self._literal_params +
            tuple([(key, doc[value]) for key, value in self._rawparams]) +
            tuple([(key, XSLT.strparam(doc[value])) for key, value in self._strparams])
        )
