import logging
import yaml
from flask import request
from .actions import SaveAction
from .rules import Rule


def get_handler(api):
    config = read_config(api)
    return Mock(api, config)


def read_config(api):
    config_file = "flows/{}.yaml".format(api)
    with open(config_file) as f:
        config = yaml.safe_load(f)
    logging.debug(f"Api configuration: {config}")
    return config


class Mock(object):

    def __init__(self, api, specs):
        self.api = api
        self.flows = [Flow(spec) for spec in specs.get("flows", [])]
        self.default_flow = Flow(specs.get("default", {}))

    def handle_request(self, method, operation, context):
        request_body = request.get_json(force=True)
        if not request_body:
            request_body = request.form
        print(request_body)
        context.setup_request(request_body)
        flow = self.get_matching_flow(method, operation)
        return flow.handle(context)

    def get_matching_flow(self, method, operation):
        flow = next((flow for flow in self.flows
                     if flow.is_match(method, operation)),
                    self.default_flow)
        logging.debug(f"Flow: {flow.route}")
        return flow


class Flow(object):

    def __init__(self, specs):
        self.route = specs.get("route")
        self.var_specs = specs.get("vars", {})
        self.rules = [Rule(spec) for spec in specs.get("rules", [])]
        self.action = SaveAction(specs.get("save", {}))

    def is_match(self, method, operation):
        expected_route = "{} /{}".format(method.upper(), operation)
        return not self.route or self.route == expected_route

    def handle(self, context):
        reference = context.get(self.var_specs.get("reference", ""))
        history = context.setup_history(reference)
        context.add_vars(self.var_specs)

        matching_rule = self.get_matching_rule(context)
        context.add_vars(matching_rule.vars)
        action = self.action.merge(matching_rule.action)
        action.perform(history, context)
        return matching_rule.get_result()

    def get_matching_rule(self, context):
        return next((rule
                     for rule in self.rules
                     if rule.is_match(context)),
                    Rule({}))


