import json
from json import JSONDecodeError
from config import app
from flask import g, render_template, request, url_for, redirect, Response
import idleonTaskSuggester

from utils import get_logger

logger = get_logger(__name__)


def format_character_name(name: str) -> str:
    name = name.strip().lower().replace(' ', '_')

    return name


def get_character_input() -> str:
    data: str = request.args.get('player') or request.form.get("player", '')

    try:
        parsed = json.loads(data)
    except JSONDecodeError:
        parsed = data

    if isinstance(parsed, str):
        parsed = format_character_name(parsed)

    if not isinstance(parsed, (str, dict)):
        raise ValueError('Submitted data neither player name nor raw data.', parsed)

    return parsed


def store_user_preferences():
    g.order_tiers = request.args.get('order_tiers', False) == 'true'


@app.route("/", defaults=dict(main_or_beta=""), methods=["GET", "POST"])
@app.route("/<main_or_beta>", methods=["GET", "POST"])
def index(main_or_beta: str) -> Response | str:
    beta = main_or_beta == 'beta'
    g.beta = beta
    page: str = 'beta/results.html' if beta else 'results.html'
    error: bool = False
    pythonOutput: list | None = None

    try:
        capturedCharacterInput: str | dict = get_character_input()
        logger.info("request.args.get('player'): %s %s", type(capturedCharacterInput), capturedCharacterInput)
        if request.method == 'POST' and isinstance(capturedCharacterInput, str):
            return redirect(url_for('index', player=capturedCharacterInput))

        store_user_preferences()

        if capturedCharacterInput:
            pythonOutput = autoReviewBot(capturedCharacterInput)

    except Exception as reason:
        logger.error('Could not get Player from Request Args: %s', reason)
        error = True

    return render_template(page, htmlInput=pythonOutput, error=error, beta=main_or_beta)


@app.route("/logtest", methods=["GET"])
def logtest():
    logger.info("Logging works")
    return "Hello, World!"


# @app.route("/")
def autoReviewBot(capturedCharacterInput) -> list | None:
    reviewInfo: list | None = None
    if capturedCharacterInput:
        reviewInfo = idleonTaskSuggester.main(capturedCharacterInput)
    # Do review stuff function, pass into array
    return reviewInfo


@app.errorhandler(404)
def page_not_found(e):
    try:
        if len(request.path) < 16:
            capturedCharacterInput = request.path[1:].strip().replace(" ", "_").lower()
            if capturedCharacterInput.find(".") == -1:
                return redirect(url_for('index', player = capturedCharacterInput))
            else:
                return redirect(url_for('index')) # Probably should get a real 404 page at some point
        else:
            return redirect(url_for('index')) # Probably should get a real 404 page at some point
    except:  # noqa
        return redirect(url_for('index')) # Probably should get a real 404 page at some point


def ensure_data(results: list):
    return bool(results)


def get_resource(dir_: str, filename: str) -> str:
    beta = "beta" if g.beta else ""
    return url_for('static', filename=f'{beta}/{dir_}/{filename}')


def style(filename: str):
    return get_resource("styles", filename)


def script(filename: str):
    return get_resource("scripts", filename)


def img(filename: str):
    return get_resource("imgs", filename)


def cards(filename: str):
    return img(f"cards/{filename}.png")


app.jinja_env.globals['ensure_data'] = ensure_data
app.jinja_env.globals['img'] = img
app.jinja_env.globals['cards'] = cards
app.jinja_env.globals['style'] = style
app.jinja_env.globals['script'] = script

if __name__ == '__main__':
    app.run()
