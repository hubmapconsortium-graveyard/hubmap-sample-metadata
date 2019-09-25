#!/usr/bin/env python
import argparse
from pathlib import Path
import json
import os

from .filler import Filler


def fill_templates(input_metadata_path, templates, target, clear_target=False):
    templates_path = Path(templates)
    target_path = Path(target)

    # Initialize template filler:
    with open(input_metadata_path) as input_metadata:
        filler = Filler(json.load(input_metadata))

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Given input JSON and a directory of templates, fill each template and save in target directory.')
    parser.add_argument(
        '--input', type=str, required=True,
        help='single JSON input file')
    parser.add_argument(
        '--template', type=str, required=True,
        help='template directory containing JSONNET files')
    parser.add_argument(
        '--target', type=str, required=True,
        help='target directory to be filled with JSON files')
    parser.add_argument(
        '--clear', action='store_true',
        help='clear target directory before regenerating?'
    )

    args = parser.parse_args()
    fill_templates(args.input, args.template, args.target, clear_target=args.clear)
