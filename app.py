import flask
from main import magic, create_logger
import datetime


app = flask.Flask(__name__)

def event_stream():
    message = magic()
    yield f'data: ' + message + '\n'\
          'retry: 60000\n'\
          '\n'


@app.route('/')
def home():
    return flask.render_template('index.html')


@app.route('/stream')
def stream():
    return flask.Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    logger = create_logger(verbose=True)
    app.debug = True
    app.run(threaded=True)
