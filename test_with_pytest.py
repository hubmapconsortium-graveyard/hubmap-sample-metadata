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
    for templates_dir in glob('workflows/*/templates-indexing'):
        templates_path = Path(templates_dir)
        inputs_path = templates_path.parent / 'outputs-hca' / 'expected'
        outputs_path = templates_path.parent / 'outputs-indexing' / 'actual'
        multi_fill_templates(inputs_path, templates_path, outputs_path, clear_target=True)


# Templates must be filled BEFORE tests are parametrized with glob;
# A setup method would run too late.
fill_templates()

@pytest.mark.parametrize('path', glob('workflows/*/outputs-indexing/actual/*'))
def test_valid_indexing_json(path):
    metadata = json.load(open(path))
    hubmap_indexing_schema = json.load(open('hubmap-indexing-schema.json'))
    validate(instance=metadata, schema=hubmap_indexing_schema)
