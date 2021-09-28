import logging
from .history import get_history


class Context(object):

    def __init__(self, api):
        self.api = api
        self.context = {}

    def setup_request(self, request):
        self.context = self.context | {"request": request}

    def setup_history(self, reference):
        history = get_history(self.api, reference)
        historical_data = history.get_data()
        self.context["history"] = historical_data
        logging.debug(f"History for api {self.api}, reference {reference}: {history}")
        return history

    def setup_vars(self, var_specs):
        for (name, path) in var_specs.items():
            value = self.get(path)
            self.add_var(name, value)

    def add_var(self, name, value):
        vars = self.context.get("vars", {})
        vars[name] = value
        logging.debug(f"Added variable {name} with value {value}")
        self.context["vars"] = vars

    def get(self, full_path):
        source, path = split_path(full_path)
        handlers = {"literal": extract_literal}
        handler = handlers.get(source, extract_static_value)
        value = handler(path, self.context.get(source, {}))

        logging.debug(f"value of {full_path} is {value}")
        return value


def split_path(path_as_string):
    path = path_as_string.split(".", 1)
    return path[0], path[1:]


def extract_static_value(path, data):
    while path:
        next_part, path = split_path(path[0])
        data = data.get(next_part, {})
    return data if data else ""


def extract_literal(literal, _):
    return literal
