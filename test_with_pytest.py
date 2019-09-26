import os
from pathlib import Path
import json
from urllib.parse import urlparse
from io import StringIO
from glob import glob

import wget
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError
import prov
import pytest

from tools.fill_templates import single_fill_templates, multi_fill_templates


def fill_templates():
    for templates_dir in glob('workflows/*/templates-hca'):
        templates_path = Path(templates_dir)
        input_path = templates_path.parent / 'inputs' / 'metadata.json'
        outputs_path = templates_path.parent / 'outputs-hca' / 'actual'
        single_fill_templates(input_path, templates_path, outputs_path, clear_target=True)
    for templates_dir in glob('workflows/*/templates-indexing'):
        templates_path = Path(templates_dir)
        inputs_path = templates_path.parent / 'outputs-hca' / 'expected'
        outputs_path = templates_path.parent / 'outputs-indexing' / 'actual'
        multi_fill_templates(inputs_path, templates_path, outputs_path, clear_target=True)


# Templates must be filled BEFORE tests are parametrized with glob;
# A setup method would run too late.
fill_templates()

# "*-*" to exclude "prov.json"
hca_paths = glob('workflows/*/outputs-hca/actual/*-*')
indexing_paths = glob('workflows/*/outputs-indexing/actual/*')
all_actual_json_paths = glob('workflows/*/outputs-*/actual/*')


@pytest.mark.parametrize('path', hca_paths)
def test_valid_any_hca_json(path):
    def download_to(url, target):
        download_path = wget.download(url)
        target_dir = os.path.dirname(target)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        os.rename(download_path, target)
    metadata = json.load(open(path))
    expected_suffix = metadata['schema_type'] + '.json'
    if not path.endswith(expected_suffix):
        self.fail(f'Expected to end with "{expected_suffix}".')
    described_by = metadata['describedBy']
    schema_url = urlparse(described_by)
    cache_path = Path('schema-cache') / schema_url.hostname / schema_url.path[1:]
    # Remove leading "/" from URL path component.
    if not os.path.isfile(cache_path):
        download_to(described_by, cache_path)
    with open(cache_path) as cache_file:
        schema = json.load(cache_file)
        validate(instance=metadata, schema=schema)


@pytest.mark.parametrize('path', hca_paths)
def test_valid_fixed_hca_json(path):
    metadata = json.load(open(path))
    hubmap_indexing_schema = json.load(open('hubmap-hca-schema.json'))
    validate(instance=metadata, schema=hubmap_indexing_schema)



@pytest.mark.parametrize('path', indexing_paths)
def test_valid_indexing_json(path):
    metadata = json.load(open(path))
    hubmap_indexing_schema = json.load(open('hubmap-indexing-schema.json'))
    validate(instance=metadata, schema=hubmap_indexing_schema)


@pytest.mark.parametrize('path', all_actual_json_paths)
def test_equality(path):
    wrapped_path = Path(path)
    with open(path) as actual_output:
        with open(wrapped_path.parent.parent / 'expected' / wrapped_path.name) as expected_output:
            assert json.load(actual_output) == json.load(expected_output)
