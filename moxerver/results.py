

class Result(object):

    def __init__(self, specs):
        # If a string value is specified, assume it's the template
        if isinstance(specs, str):
            specs = {"template": specs}
        self.template = specs.get("template")
        self.status_code = specs.get("status_code")

    def __repr__(self):
        return f"Result: {self.status_code} {self.template}"

    def get_template(self):
        return self.template

    def get_status_code(self):
        if self.status_code:
            # If there is one, return it
            return self.status_code
        if self.template:
            # if none set, but there is a template, default to 200
            return 200
        # Default to 404 otherwise
        return 404
