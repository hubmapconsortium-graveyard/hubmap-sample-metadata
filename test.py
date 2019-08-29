#!/usr/bin/env python

import os
import json
from urllib.parse import urlparse

import wget
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

fails = {}


def download_to(url, target):
    download_path = wget.download(url)
    target_dir = os.path.dirname(target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    os.rename(download_path, target)


def main():
    for dir_path, _, file_names in os.walk('workflows'):
        for name in file_names:
            if not name.endswith('.json') or 'TODO' in name:
                print(f'Skip: {name}')
                continue
            path = os.path.join(dir_path, name)
            print(f'Load: {path}')
            metadata = json.load(open(path))
            expected_suffix = metadata['schema_type'] + '.json'
            if not name.endswith(expected_suffix):
                fails[name] = f'Expected to end with "{expected_suffix}".'
                continue
            described_by = metadata['describedBy']
            schema_url = urlparse(described_by)
            cache_path = f'schema-cache/{schema_url.hostname}{schema_url.path}'
            print(f'Check cache: {cache_path}')
            if not os.path.isfile(cache_path):
                download_to(described_by, cache_path)
            schema = json.load(open(cache_path))
            try:
                validate(instance=metadata, schema=schema)
            except (ValidationError, SchemaError) as e:
                fails[name] = e
    if fails:
        print(fails)
        exit(1)
    else:
        print('PASS!')


if __name__ == '__main__':
    main()
