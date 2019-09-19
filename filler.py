from _jsonnet import evaluate_file


class Filler():
    def fill(self, template_path, dest_path):
        filled_template = evaluate_file(str(template_path))
        with open(dest_path, 'w') as dest:
            dest.write(filled_template)
