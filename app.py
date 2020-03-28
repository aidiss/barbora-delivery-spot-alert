import flask
from flask_caching import Cache
from main import magic, create_logger
import datetime
config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 10
}


app = flask.Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

def event_stream():
    # now = datetime.datetime.now()
    # if last_now is None now:
    #     last_now = now

    message = magic()
    yield f'data: ' + message + '\n'\
          'retry: 60000\n'\
          '\n'


@app.route('/')
def home():
    return flask.render_template('index.html')


@app.route('/stream')
# @cache.cached(timeout=10)
def stream():
    return flask.Response(event_stream(), mimetype="text/event-stream")



if __name__ == '__main__':
    logger = create_logger(verbose=True)

    app.debug = True
    app.run(threaded=True)
