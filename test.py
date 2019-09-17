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


class TestsContainer(unittest.TestCase):
    hubmap_schema = json.load(open('hubmap-schema.json'))


def make_json_test(description, dir_path, name):
    def test(self):
        with open(Path(dir_path) / name) as json_fixture:
            metadata = json.load(json_fixture)
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


def drop_blank(lines):
    return set(line for line in lines if line.strip())


def make_prov_test(description, dir_path, name):
    def test(self):
        rdf_path = Path(dir_path) / name
        provenance = prov.read(rdf_path, format='rdf')
        output = StringIO()
        serializer = prov.serializers.provn.ProvNSerializer(provenance)
        serializer.serialize(output)
        actual = output.getvalue()
        actual_lines = drop_blank(actual.split('\n'))

        with open(Path(dir_path) / 'prov.prov') as prov_fixture:
            expected_lines = drop_blank(prov_fixture.read().split('\n'))
            self.assertEqual(
                actual_lines, expected_lines,
                msg=f'Copying this to prov.prov might fix the problem:\n{actual}'
            )
    return test


def download_to(url, target):
    download_path = wget.download(url)
    target_dir = os.path.dirname(target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.rename(download_path, target)


if __name__ == '__main__':
    for dir_path, _, file_names in os.walk('workflows'):
        for name in sorted(file_names):
            if 'TODO' in name:
                print(f'TODO: {name}')
            elif name.endswith('.json'):
                test_function = make_json_test('name', dir_path, name)
                setattr(TestsContainer, 'test_' + name, test_function)
            elif name == 'prov.rdf':
                test_function = make_prov_test('name', dir_path, name)
                setattr(TestsContainer, 'test_' + name, test_function)
    unittest.main(verbosity=2)
