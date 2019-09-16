#!/usr/bin/env python

import os
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


def validate_json(dir_path, name, fails, hubmap_schema):
    print(f'\tLoad JSON: {name}')
    path = os.path.join(dir_path, name)
    metadata = json.load(open(path))
    expected_suffix = metadata['schema_type'] + '.json'
    if not name.endswith(expected_suffix):
        fails[path]['suffix'] = f'Expected to end with "{expected_suffix}".'
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
        fails[path]['hca'] = e
    try:
        validate(instance=metadata, schema=hubmap_schema)
    except (ValidationError, SchemaError) as e:
        fails[path]['hubmap'] = e


def validate_prov(dir_path, name, fails):
    print(f'\tLoad Provenance: {name}')
    path = os.path.join(dir_path, name)
    provenance = prov.read(path, format='rdf')
    output = StringIO()
    serializer = prov.serializers.provn.ProvNSerializer(provenance)
    serializer.serialize(output)
    print(indent(output.getvalue(), '\t'))


def main():
    fails = defaultdict(dict)
    hubmap_schema = json.load(open('hubmap-schema.json'))
    for dir_path, _, file_names in os.walk('workflows'):
        print(f'Testing: {dir_path}')
        for name in sorted(file_names):
            if 'TODO' in name:
                print(f'\tTODO: {name}')
            elif name.endswith('.json'):
                validate_json(dir_path, name, fails, hubmap_schema)
            elif name == 'prov.rdf':
                validate_prov(dir_path, name, fails)
    if fails:
        PrettyPrinter(width=100).pprint(dict(fails))
        print('FAIL!')
        exit(1)
    else:
        print('PASS!')


if __name__ == '__main__':
    main()
