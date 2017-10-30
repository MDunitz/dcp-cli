import base64
import json
import os
import sys
import unittest
import uuid

import boto3
import tweak
from moto import mock_s3

from ... import reset_tweak_changes

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from hca import upload
from .. import TEST_UPLOAD_BUCKET, mock_current_upload_area, setup_tweak_config


class TestUploadFileUpload(unittest.TestCase):

    @mock_s3
    @reset_tweak_changes
    def test_file_upload(self):
        setup_tweak_config()
        area = mock_current_upload_area()
        s3 = boto3.resource('s3')
        s3.Bucket(TEST_UPLOAD_BUCKET).create()

        upload.upload_file('LICENSE')

        obj = s3.Bucket(TEST_UPLOAD_BUCKET).Object("{}/LICENSE".format(area.uuid))
        with open('LICENSE', 'rb') as fh:
            expected_contents = fh.read()
            self.assertEqual(obj.get()['Body'].read(), expected_contents)

    @mock_s3
    @reset_tweak_changes
    def test_file_upload_with_target_filename_option(self):
        setup_tweak_config()
        area = mock_current_upload_area()
        s3 = boto3.resource('s3')
        s3.Bucket(TEST_UPLOAD_BUCKET).create()

        upload.upload_file('LICENSE', target_filename='POO')

        obj = s3.Bucket(TEST_UPLOAD_BUCKET).Object("{}/POO".format(area.uuid))
        with open('LICENSE', 'rb') as fh:
            expected_contents = fh.read()
            self.assertEqual(obj.get()['Body'].read(), expected_contents)
