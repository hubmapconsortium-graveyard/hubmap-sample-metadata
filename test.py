#!/usr/bin/env python

import os
from pathlib import Path
import json
from urllib.parse import urlparse
from io import StringIO
import unittest

import wget
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError
import prov

from tools.fill_templates import fill_templates


class BaseTestCase(unittest.TestCase):
    hubmap_schema = json.load(open('hubmap-schema.json'))


def make_skip_test(description):
    def test(self):
        self.skipTest(description)
    return test


def make_validity_test(description, dir_path, name):
    def test(self):
        with open(dir_path / name) as json_output:
            metadata = json.load(json_output)
            expected_suffix = metadata['schema_type'] + '.json'
            if not name.endswith(expected_suffix):
                self.fail(f'Expected to end with "{expected_suffix}".')
            described_by = metadata['describedBy']
            schema_url = urlparse(described_by)
            cache_path = Path('schema-cache') / schema_url.hostname / schema_url.path[1:]
            # Remove leading "/" from URL path component.
            if not os.path.isfile(cache_path):
                download_to(described_by, cache_path)
            with open(cache_path) as cache_file:
                schema = json.load(cache_file)
                try:
                    validate(instance=metadata, schema=schema)
                except (ValidationError, SchemaError) as e:
                    self.fail(e)
                try:
                    validate(instance=metadata, schema=self.hubmap_schema)
                except (ValidationError, SchemaError) as e:
                    self.fail(e)
    return test


def make_equality_test(description, dir_path, name):
    def test(self):
        with open(dir_path / name) as actual_output:
            with open(dir_path.parent / 'expected' / name) as expected_output:
                self.assertEqual(
                    json.load(actual_output),
                    json.load(expected_output)
                )
    return test


def drop_blank(lines):
    return set(line for line in lines if line.strip())


def make_prov_test(description, dir_path, name):
    def test(self):
        prov_json_path = dir_path / name
        provenance = prov.read(prov_json_path, format='json')
        output = StringIO()
        # In production, we won't output PROV-N,
        # but for tests, it's easy for a human to read, and easy to compare.
        serializer = prov.serializers.provn.ProvNSerializer(provenance)
        serializer.serialize(output)
        actual = output.getvalue()
        actual_lines = drop_blank(actual.split('\n'))

        with open(dir_path.parent / 'expected.prov') as prov_fixture:
            expected_lines = drop_blank(prov_fixture.read().split('\n'))
            self.assertEqual(
                actual_lines, expected_lines,
                msg=f'Expected this PROV:\n{actual}'
            )
    return test


def download_to(url, target):
    download_path = wget.download(url)
    target_dir = os.path.dirname(target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.rename(download_path, target)


def fill_templates_hca(path):
    for dir, _, file_names in os.walk(path):
        dir_path = Path(dir)
        if dir_path.name != 'templates-hca':
            continue
        input_path = dir_path.parent / 'inputs' / 'metadata.json'
        outputs_path = dir_path.parent / 'outputs-hca' / 'actual'
        fill_templates(input_path, dir_path, outputs_path, clear_target=True)


def test_outputs(path):
    # Dynamic test creation based on:
    # https://eli.thegreenplace.net/2014/04/02/dynamically-generating-python-test-cases
    for dir, _, file_names in os.walk(path):
        dir_path = Path(dir)
        if dir_path.name != 'expected':
            continue
        dynamic_class_name = f'Test\t{dir_path}'
        DynamicTestCase = type(dynamic_class_name, (BaseTestCase,), {})
        globals()[dynamic_class_name] = DynamicTestCase
        for name in sorted(file_names):
            if name == 'prov.json':
                setattr(DynamicTestCase, 'test_prov\t' + name,
                        make_prov_test('name', dir_path, name))
            elif name.endswith('.json'):
                setattr(DynamicTestCase, 'test_validity\t' + name,
                        make_validity_test('name', dir_path, name))
                setattr(DynamicTestCase, 'test_equality\t' + name,
                        make_equality_test('name', dir_path, name))
            else:
                raise Exception(f'Unexpected file type: "{name}"')


if __name__ == '__main__':
    target = 'workflows'
    fill_templates_hca(target)
    # fill_templates_indexing(target)
    test_outputs(target)
    # test_outputs_indexing(target)

    unittest.main(verbosity=2)
