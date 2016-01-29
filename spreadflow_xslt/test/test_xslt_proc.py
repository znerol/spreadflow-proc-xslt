from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os
import copy

from twisted.internet import defer

from mock import Mock
from testtools import TestCase, run_test_with
from testtools.twistedsupport import AsynchronousDeferredRunTest

from spreadflow_core.scheduler import Scheduler
from spreadflow_delta.test.matchers import MatchesSendDeltaItemInvocation

from spreadflow_xslt.proc import XSLT

FIXTURE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

class XSLTTransformUnitTest(TestCase):

    @run_test_with(AsynchronousDeferredRunTest)
    @defer.inlineCallbacks
    def test_spec_document_example(self):
        """
        Operates on fixtures/01-spec-document-example.*
        see: https://www.w3.org/TR/xslt#section-Examples
        """
        xsl_path = os.path.join(FIXTURE_DIRECTORY, '01-spec-document-example.xsl')
        pipe = XSLT(xsl_path)

        input_data = b''
        input_path = os.path.join(FIXTURE_DIRECTORY, '01-spec-document-example.xml')
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()

        expected_data = b''
        expected_path = os.path.join(FIXTURE_DIRECTORY, '01-spec-document-example.html')
        with open(expected_path, 'rb') as expected_file:
            expected_data = expected_file.read()

        item = {
            'inserts': ['a'],
            'deletes': [],
            'data': {
                'a': {
                    'content': input_data
                }
            }
        }

        expected = copy.deepcopy(item)
        expected['data']['a']['transformed'] = expected_data

        matches = MatchesSendDeltaItemInvocation(expected, pipe)
        send = Mock(spec=Scheduler.send)
        yield pipe(item, send)
        self.assertEquals(send.call_count, 1)
        self.assertThat(send.call_args, matches)

    @run_test_with(AsynchronousDeferredRunTest)
    @defer.inlineCallbacks
    def test_spec_data_example(self):
        """
        Operates on fixtures/02-spec-data-example.*
        see: https://www.w3.org/TR/xslt#section-Examples
        """
        xsl_path = os.path.join(FIXTURE_DIRECTORY, '02-spec-data-example.xsl')
        pipe = XSLT(xsl_path, key='custom_content', destkey='custom_result', coiterate=None)

        input_data = b''
        input_path = os.path.join(FIXTURE_DIRECTORY, '02-spec-data-example.xml')
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()

        expected_data = b''
        expected_path = os.path.join(FIXTURE_DIRECTORY, '02-spec-data-example.html')
        with open(expected_path, 'rb') as expected_file:
            expected_data = expected_file.read()

        item = {
            'inserts': ['b'],
            'deletes': [],
            'data': {
                'b': {
                    'custom_content': input_data
                }
            }
        }

        expected = copy.deepcopy(item)
        expected['data']['b']['custom_result'] = expected_data

        matches = MatchesSendDeltaItemInvocation(expected, pipe)
        send = Mock(spec=Scheduler.send)
        yield pipe(item, send)
        self.assertEquals(send.call_count, 1)
        self.assertThat(send.call_args, matches)
