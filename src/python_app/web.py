from flask import Flask, render_template

from python_app.routes.characters import characters
from python_app.routes.home import home
from python_app.routes.scores import scores


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(home)
    app.register_blueprint(scores)
    app.register_blueprint(characters)
    return app


def main() -> None:
    create_app().run(host="0.0.0.0", port=5000)
