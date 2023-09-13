from flask import Flask, request, g, render_template, abort, Response
from moxerver.handler import get_handler
from moxerver.context import Context
from moxerver.history import History
from moxerver.db import get_db, ensure_path
import json
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)


@app.route("/mox/<api>/<path:subpath>", methods=["POST", "GET"])
def execute_mock(api, subpath):
    method = request.method
    logging.info(f"Received request to {method} {api}/{subpath}")

    context = Context(api)
    mock = get_handler(api)
    result = mock.handle_request(method, subpath, context)
    logging.info(f"Result {result}")

    template, status_code = interpret_result(api, result)
    return render_template(template, **context.context), status_code


def interpret_result(api, result):
    status_code = result.get_status_code()
    if result.get_template():
        return "{}/{}".format(api, result.template), status_code
    abort(status_code)


@app.route("/history/<api>/<reference>")
def show_history(api, reference):
    history = History(api, reference)
    data = history.get_data()
    return Response(json.dumps(data))


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.cli.command("init_db")
def init_db():
    with app.app_context():
        ensure_path()
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
