import logging
from .actions import SaveAction
from .results import Result


class Rule(object):

    def __init__(self, specs):
        self.filter_specs = specs.get("filter", {})
        self.action = SaveAction(specs.get("save", {}))
        self.result = Result(specs.get("result", {}))

    def is_match(self, context):
        logging.debug(f"Rules: {self.filter_specs}")
        matches = [context.get(path) == expected_value
                   for (path, expected_value) in self.filter_specs.items()]
        return all(matches)

    def get_result(self):
        return self.result



