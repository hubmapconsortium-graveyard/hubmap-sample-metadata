from shutil import copy


class Filler():
    def __init__(self, metadata):
        self.metadata = metadata

    def fill(self, template_path, dest_path):
        # TODO: Fill templates, instead of just copying.
        copy(template_path, dest_path)
