import json

from _jsonnet import evaluate_file


class Filler():
    def __init__(self, metadata):
        self.metadata = metadata

    def fill(self, template_path, dest_path):
        # Perhaps reflecting the command-line interface,
        # all in the ways of passing in data are dicts of strings.
        # `tla_codes` can actually handle arbitrary jsonnet,
        # of which json is a subset.
        filled_template = evaluate_file(
            str(template_path),
            tla_codes={'_': json.dumps(self.metadata)}
        )
        with open(dest_path, 'w') as dest:
            dest.write(filled_template)
