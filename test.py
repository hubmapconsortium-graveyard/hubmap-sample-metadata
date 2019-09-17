#!/usr/bin/env python

import os
from pathlib import Path
import json
from urllib.parse import urlparse
from collections import defaultdict
from pprint import PrettyPrinter
from io import StringIO
from textwrap import indent

import wget
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError
import prov


def download_to(url, target):
    download_path = wget.download(url)
    target_dir = os.path.dirname(target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.rename(download_path, target)


class TestLogger():
    def __init__(self):
        self.hubmap_schema = json.load(open('hubmap-schema.json'))
        self.fails = defaultdict(dict)

    def validate_json(self, dir_path, name):
        print(f'\tLoad JSON: {name}')
        path = Path(dir_path) / name
        metadata = json.load(open(path))
        expected_suffix = metadata['schema_type'] + '.json'
        if not name.endswith(expected_suffix):
            self.fails[path]['suffix'] = f'Expected to end with "{expected_suffix}".'
            return
        described_by = metadata['describedBy']
        schema_url = urlparse(described_by)
        cache_path = f'schema-cache/{schema_url.hostname}{schema_url.path}'
        if not os.path.isfile(cache_path):
            download_to(described_by, cache_path)
        schema = json.load(open(cache_path))
        try:
            validate(instance=metadata, schema=schema)
        except (ValidationError, SchemaError) as e:
            self.fails[path]['hca'] = e
        try:
            validate(instance=metadata, schema=self.hubmap_schema)
        except (ValidationError, SchemaError) as e:
            self.fails[path]['hubmap'] = e

    def validate_prov(self, dir_path, name):
        print(f'\tLoad Provenance: {name}')
        path = Path(dir_path) / name
        provenance = prov.read(path, format='rdf')
        output = StringIO()
        serializer = prov.serializers.provn.ProvNSerializer(provenance)
        serializer.serialize(output)
        print(indent(output.getvalue(), '\t'))


def main():
    logger = TestLogger()
    for dir_path, _, file_names in os.walk('workflows'):
        print(f'Testing: {dir_path}')
        for name in sorted(file_names):
            if 'TODO' in name:
                print(f'\tTODO: {name}')
            elif name.endswith('.json'):
                logger.validate_json(dir_path, name)
            elif name == 'prov.rdf':
                logger.validate_prov(dir_path, name)
    if logger.fails:
        PrettyPrinter(width=100).pprint(dict(logger.fails))
        print('FAIL!')
        exit(1)
    else:
        print('PASS!')


if __name__ == '__main__':
    main()
