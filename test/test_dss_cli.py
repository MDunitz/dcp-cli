#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import unittest
from io import open
import subprocess

import six

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, pkg_root)

import hca.dss
import hca.dss.cli
import hca.dss.regenerate_api
import hca.dss.constants
from test.config import override_oauth_config  # noqa


class TestDssCLI(unittest.TestCase):
    """Test the entire module."""

    def test_make_name(self):
        """Test make_name in parser.py."""
        http_method = "get"
        path_split = ["bundles"]
        self.assertEqual(
            hca.dss.regenerate_api._make_name(http_method, path_split),
            "get-bundles"
        )

        path_split.append("cmd")
        self.assertEqual(
            hca.dss.regenerate_api._make_name(http_method, path_split),
            "get-bundles-cmd"
        )

    def test_index_parameters(self):
        """Test index_parameters in parser.py."""
        self.maxDiff = None

        params = {
            "description": "Returns a list of bundles matching given criteria.\n",
            "responses": {
              "200": {
                "description": "OK",
                "schema": {
                  "properties": {
                    "bundles": {
                      "items": {
                        "$ref": "#/definitions/Bundle"
                      },
                      "type": "array"
                    }
                  },
                  "required": [
                    "bundles"
                  ],
                  "type": "object"
                }
              }
            },
            "summary": "Query bundles"
        }
        self.assertEqual(hca.dss.regenerate_api.index_parameters(None, params), {})

        params["parameters"] = [
            {
                "description": "Bundle unique ID.",
                "in": "path",
                "name": "uuid",
                "required": True,
                "type": "string",
            }
        ]
        self.assertEqual(
            hca.dss.regenerate_api.index_parameters(None, params),
            {"uuid": {
                "description": "Bundle unique ID.",
                "in": "path",
                "name": "uuid",
                "required": True,
                "type": "string",
                "array": False,
                'req': True,
                'hierarchy': ['uuid']
            }})

        params['parameters'] = [{
            "in": "body",
            "name": "extras",
            "required": True,
            "schema": {
              "properties": {
                "bundle_uuid": {
                  "description": "A RFC4122-compliant ID.",
                  "type": "string"
                },
                "timestamp": {
                  "description": "Timestamp of file creation in RFC3339.",
                  "format": "date-time",
                  "type": "string"
                }
              },
              "required": [
                "bundle_uuid",
              ],
              "type": "object"
            }
          }
        ]
        self.assertEqual(
            hca.dss.regenerate_api.index_parameters(None, params),
            {"timestamp": {
                "description": "Timestamp of file creation in RFC3339.",
                "in": "body",
                "name": "timestamp",
                "type": "string",
                "format": "date-time",
                "array": False,
                'req': False,
                'hierarchy': ['timestamp']
            },
            "bundle_uuid": {
                "description": "A RFC4122-compliant ID.",
                "in": "body",
                "name": "bundle_uuid",
                "type": "string",
                "array": False,
                'req': True,
                'hierarchy': ['bundle_uuid']
            },
            'top_level_body_params': {
                "timestamp": {
                    "description": "Timestamp of file creation in RFC3339.",
                    "in": "body",
                    "name": "timestamp",
                    "type": "string",
                    "format": "date-time",
                    "array": False,
                    'req': False,
                    'hierarchy': ['timestamp']
                },
                "bundle_uuid": {
                    "description": "A RFC4122-compliant ID.",
                    "in": "body",
                    "name": "bundle_uuid",
                    "type": "string",
                    "array": False,
                    'req': True,
                    'hierarchy': ['bundle_uuid']
            }}}
        )

    def test_get_files_cli(self):
        """Testing 2 things: 1. Printing bytes to stdout; 2. Iterative content download."""

        dirpath = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dirpath, "bundle", "SRR2967608_1.fastq.gz")

        self.assertGreater(os.stat(file_path).st_size, hca.dss.constants.Constants.CHUNK_SIZE)

        args = {'file_or_dir': [file_path],
                'replica': "aws",
                'staging_bucket': "org-humancellatlas-dss-cli-test"}
        response = hca.dss.upload(**args)

        file_uuid = response['files'][0]['uuid']

        process = subprocess.Popen(["hca", "get-files", file_uuid, "--replica", "aws"], stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.assertIsInstance(stdout, bytes)
        with open(file_path, "rb") as bytes_fh:
            file_content = bytes_fh.read()
            if file_content != stdout:
                self.fail("output does not match file content: \"%s\"" % stdout)

    def test_parsing(self):
        """Test that the parser parses arguments correctly."""

        cli = hca.dss.cli.CLI()

        args = ["put-files", "134", "--bundle-uuid", "asdf", "--creator-uid", "1", "--source-url", "sljdf.com"]
        expected = {'source_url': 'sljdf.com', 'bundle_uuid': 'asdf', 'uuid': '134', 'creator_uid': 1}
        func, api_args = cli.parse_args(args)
        self.assertEqual(api_args, expected)

        args = ["put-files", "--bundle-uuid", "asdf", "--creator-uid", "1", "--source-url", "sljdf.com", "134"]
        func, api_args = cli.parse_args(args)
        self.assertEqual(api_args, expected)

        args = ["put-files", "--creator-uid", "1", "--source-url", "sljdf.com", "134"]
        process = subprocess.Popen(["hca"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        expected_error = '--bundle-uuid is required' if six.PY2 else 'are required: --bundle-uuid'
        six.assertRegex(self, stderr.decode('utf8'), expected_error)

        args = ["put-files", "--bundle-uuid", "asdf", "--creator-uid", "1", "--source-url", "sljdf.com"]
        process = subprocess.Popen(["hca"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        expected_error = 'too few arguments' if six.PY2 else 'are required: uuid'
        six.assertRegex(self, stderr.decode('utf8'), expected_error)

        args = ["put-files", "--bundle-uuid", "--creator-uid", "1", "--source-url", "sljdf.com", "134"]
        process = subprocess.Popen(["hca"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        six.assertRegex(self, stderr.decode('utf8'), '--bundle-uuid: expected one argument')

        args = ["get-bundles", "uuid_arg"]
        expected = {"uuid": "uuid_arg"}
        func, api_args = cli.parse_args(args)
        self.assertEqual(api_args, expected)

        args = ["get-bundles", "uuid_arg", "--version", "version_arg", "--replica", "rep"]
        expected = {"uuid": "uuid_arg", "replica": "rep", "version": "version_arg"}
        func, api_args = cli.parse_args(args)
        self.assertEqual(api_args, expected)

        # Works for now but shouldn't in the future b/c --replica required when uuid and version specified.
        args = ["get-bundles", "uuid_arg", "--version", "version_arg"]
        expected = {"uuid": "uuid_arg", "version": "version_arg"}
        func, api_args = cli.parse_args(args)
        self.assertEqual(api_args, expected)

        # Works for now. --replica isn't an option unless both uuid and version specified.
        args = ["get-bundles", "uuid_arg", "--replica", "rep"]
        expected = {"uuid": "uuid_arg", "replica": "rep"}
        func, api_args = cli.parse_args(args)
        self.assertEqual(api_args, expected)

    def _get_first_url(self, response):
        """Get the first url we sent a request to if there were redirects."""
        if response.history:
            return response.history[0].url
        return response.url

    def test_requests(self):
        """Test that the parser parses arguments in the right way."""

        cli = hca.dss.cli.CLI()

        args = ["get-bundles", "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA", "--version", "1981-07-21T11:35:45+00:00", "--replica", "aws"]
        response = cli.make_request(args)
        self.assertFalse(response.ok)  # The key is not in there

        args = ["get-bundles", "AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA", "--version", "version_arg"]
        response = cli.make_request(args)
        self.assertEqual(
            self._get_first_url(response),
            "https://hca-dss.czi.technology/v1/bundles/AAAAAAAA-AAAA-AAAA-AAAA-AAAAAAAAAAAA?version=version_arg"
        )
        self.assertFalse(response.ok)

    @unittest.skip("We don't generate bindings from test files right now and there are no references in " +
                   "the path parameters of our swagger spec. Need to refactor this test.")
    def test_refs(self):
        """Test internal JSON reference resolution."""
        cli = hca.dss.cli.CLI()
        args = ["put-reftest", "--name", "name", "--uuid", "uuid", "--versions", "item1", "item2"]
        out = {"name": "name", "uuid": "uuid", "versions": ["item1", "item2"]}
        self.assertEqual(cli.parse_args(args), out)

    def test_cli_login(self):
        from tweak import Config

        cli = hca.dss.cli.CLI()

        access_token = "test_access_token"
        out = {'completed': True}
        args = ["login", "--access-token", access_token]

        with override_oauth_config():
            response = cli.make_request(args)
            config = Config(hca.dss.constants.Constants.TWEAK_PROJECT_NAME)

            self.assertEqual(response, out)
            self.assertEqual(config.access_token, access_token)

    def test_array_cli(self):
        """Ensure that this framework can handle arrays."""

        cli = hca.dss.cli.CLI()
        args = ["put-bundles", "uuid", "--version", "version", "--files", "uuid1/v1/n1/True", "uuid2/v2/n2/False", "--creator-uid", "3", "--replica", "rep"]
        out = {"uuid": "uuid", "version": "version", "files": ["uuid1/v1/n1/True", "uuid2/v2/n2/False"], "creator_uid": 3, "replica": "rep"}
        func, api_args = cli.parse_args(args)
        self.assertEqual(api_args, out)

    def test_parsing_array_object_literals(self):
        """Make sure that parsing literals works within an array object."""
        from hca.dss.autogenerated.put_bundles import PutBundles  # noqa

        cli = hca.dss.cli.CLI()
        args = ["put-bundles", "234sf", "--files", "True/n1/u1/v1", "False/n2/u2/v2", "--replica" ,"rep", "--creator-uid", "8"]
        func, parsed_args = cli.parse_args(args)
        out = {'files': [{'indexed': True, 'version': 'v1', 'uuid': 'u1', 'name': 'n1'}, {'indexed': False, 'version': 'v2', 'uuid': 'u2', 'name': 'n2'}], 'creator_uid': 8}
        body_payload = PutBundles._build_body_payload(parsed_args)
        self.assertEqual(body_payload, out)

    @unittest.skip("This doesn't work because https://github.com/HumanCellAtlas/data-store/pull/167 not merged yet.")
    def test_json_input(self):
        """Ensure that adding json input works."""
        cli = hca.dss.cli.CLI()
        args = ["post-search", "--query", '{"hello":"world", "goodbye":"earth"}']
        parsed_args = cli.parse_args(args)
        out = {"query": {"hello": "world", "goodbye": "earth"}}
        self.assertEqual(out, parsed_args)

    @unittest.skip("The bundle referenced in this test is no longer in place. Plans to set up an upload bundle")
    def test_upload_to_cloud_from_s3(self):
        import hca.dss.upload_to_cloud
        uuids, names = hca.dss.upload_to_cloud.upload_to_cloud(
            ["s3://hca-dss-test-src/data-bundles-examples/import/10x/pbmc8k/bundles/bundle1/"],
            "pointless-staging-bucket",
            "aws",
            True
        )
        out = [
            "data-bundles-examples/import/10x/pbmc8k/bundles/bundle1/assay.json",
            "data-bundles-examples/import/10x/pbmc8k/bundles/bundle1/project.json",
            "data-bundles-examples/import/10x/pbmc8k/bundles/bundle1/sample.json"
        ]
        self.assertEqual(len(uuids), len(names))
        assert_list_items_equal = (self.assertCountEqual if six.PY3
                                   else self.assertItemsEqual)
        assert_list_items_equal(names, out)


if __name__ == '__main__':
    unittest.main()