from _jsonnet import evaluate_file


class Filler():
    def __init__(self, metadata):
        self.metadata = metadata

    def fill(self, template_path, dest_path):
        # TODO: Fill templates with metadata
        filled_template = evaluate_file(str(template_path))
        with open(dest_path, 'w') as dest:
            dest.write(filled_template)
