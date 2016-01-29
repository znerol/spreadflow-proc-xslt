from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os
import copy

from defusedxml import lxml as etree
from lxml.etree import XSLT
from twisted.internet import defer

from mock import Mock, call, patch, DEFAULT
from testtools import TestCase, run_test_with
from testtools.twistedsupport import AsynchronousDeferredRunTest

from spreadflow_core.scheduler import Scheduler
from spreadflow_delta.test.matchers import MatchesSendDeltaItemInvocation

from spreadflow_xslt.proc import XsltPipeline

FIXTURE_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')

class XsltPipelineStartUnitTest(TestCase):

    @patch('glob.glob')
    @patch('os.path.isdir')
    @patch('spreadflow_xslt.proc.XsltPipeline._load_file')
    def test_start_single_file(self, load_file, isdir, glob):
        isdir.configure_mock(return_value=False)

        pipe = XsltPipeline('/path/to/style.xslt')
        pipe.start()

        isdir.assert_called_once_with('/path/to/style.xslt')
        load_file.assert_called_once_with('/path/to/style.xslt')
        glob.assert_not_called()

    @patch('glob.glob')
    @patch('os.path.isdir')
    @patch('spreadflow_xslt.proc.XsltPipeline._load_file')
    def test_start_dir(self, load_file, isdir, glob):
        isdir.configure_mock(return_value=True)
        glob.configure_mock(side_effect=[
            [
                '/path/to/directory/a.xsl',
                '/path/to/directory/c.XSL',
            ],
            [
                '/path/to/directory/B.xslt',
            ]
        ])

        pipe = XsltPipeline('/path/to/directory')
        pipe.start()

        isdir.assert_called_once_with('/path/to/directory')
        glob.assert_has_calls([
            call('/path/to/directory/*.xsl'),
            call('/path/to/directory/*.xslt'),
        ])
        load_file.assert_has_calls([
            call('/path/to/directory/a.xsl'),
            call('/path/to/directory/B.xslt'),
            call('/path/to/directory/c.XSL'),
        ])


class XsltPipelineTransformUnitTest(TestCase):

    @run_test_with(AsynchronousDeferredRunTest)
    @defer.inlineCallbacks
    def test_spec_document_example(self):
        """
        Operates on fixtures/01-spec-document-example.*
        see: https://www.w3.org/TR/xslt#section-Examples
        """
        pipe = XsltPipeline('/dev/null')

        input_data = b''
        input_path = os.path.join(FIXTURE_DIRECTORY, '01-spec-document-example.xml')
        with open(input_path, 'r') as input_file:
            input_data = input_file.read()

        expected_data = b''
        expected_path = os.path.join(FIXTURE_DIRECTORY, '01-spec-document-example.html')
        with open(expected_path, 'r') as expected_file:
            expected_data = expected_file.read()

        xsl_path = os.path.join(FIXTURE_DIRECTORY, '01-spec-document-example.xsl')
        pipe.transformers = [
            XSLT(etree.parse(xsl_path))
        ]

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
        pipe = XsltPipeline('/dev/null', key='custom_content', destkey='custom_result')


        input_data = b''
        input_path = os.path.join(FIXTURE_DIRECTORY, '02-spec-data-example.xml')
        with open(input_path, 'r') as input_file:
            input_data = input_file.read()

        expected_data = b''
        expected_path = os.path.join(FIXTURE_DIRECTORY, '02-spec-data-example.html')
        with open(expected_path, 'r') as expected_file:
            expected_data = expected_file.read()

        xsl_path = os.path.join(FIXTURE_DIRECTORY, '02-spec-data-example.xsl')
        pipe.transformers = [
            XSLT(etree.parse(xsl_path))
        ]

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
