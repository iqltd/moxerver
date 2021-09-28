

class SaveAction(object):

    def __init__(self, specs):
        self.specs = specs

    def merge(self, action):
        merged_specs = self.specs | action.specs
        return SaveAction(merged_specs)

    def perform(self, history, context):
        data = {name: context.get(path)
                for (name, path) in self.specs.items()}
        if data:
            history.persist_data(data)
