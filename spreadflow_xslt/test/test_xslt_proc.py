from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from mock import Mock, call, patch, DEFAULT
from testtools import TestCase

from spreadflow_core.scheduler import Scheduler
from spreadflow_delta.test.matchers import MatchesSendDeltaItemInvocation

from spreadflow_xslt.proc import XsltPipeline

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
