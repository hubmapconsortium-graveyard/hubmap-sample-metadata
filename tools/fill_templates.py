from pathlib import Path
import json
import os
import re

from .filler import Filler


def _fill_templates_with_dict(input_dict, templates, target, clear_target=False):
    templates_path = Path(templates)
    target_path = Path(target)

    # Initialize template filler:
    filler = Filler(input_dict)

    # Optionally, clear outputs from previous run:
    if clear_target:
        for file in os.listdir(target_path):
            if file != '.gitignore':
                os.remove(target_path / file)

    # And fill it up again:
    for name in os.listdir(templates_path):
        if not name.endswith('.jsonnet'):
            raise Exception(f'Expected only ".jsonnet" files in "{templates_path}", not "{name}"')
        if 'TODO' in name:
            continue
        json_name = name.replace('.jsonnet', '.json')
        filler.fill(templates_path / name, target_path / json_name)


def single_fill_templates(input_metadata_path, templates, target, clear_target=False):
    '''Given a single input and multiple templates, fill out each template.'''
    with open(input_metadata_path) as input_metadata:
        input_dict = json.load(input_metadata)
    _fill_templates_with_dict(input_dict, templates, target)


def multi_fill_templates(inputs, templates, target, clear_target=False):
    '''Given multiple inputs and multiple templates, combine the inputs and fill the templates.'''
    input_dict = {}
    for filename in os.listdir(inputs):
        with open(Path(inputs) / filename) as input_json:
            stem = re.sub(r'(?:^\d+-)?(.+)\.json$', r'\1', filename)
            input_dict[stem] = json.load(input_json)
    _fill_templates_with_dict(input_dict, templates, target)
