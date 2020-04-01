import datetime
import sys

import flask

from main import create_logger, magic

app = flask.Flask(__name__, static_folder='static')


def event_stream():
    message = magic(HEADERS)
    yield f"data: {message}\nretry: 60000\n\n"


@app.route("/")
def home():
    return flask.render_template("index.html")


@app.route("/stream")
def stream():
    return flask.Response(event_stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    logger = create_logger(verbose=True)
    try:
        HEADERS = sys.argv[1]
    except IndexError as _:
        print("Please provide path tu raw headers file as an argument")
        sys.exit(1)
    app.debug = False
    app.run(threaded=True)
