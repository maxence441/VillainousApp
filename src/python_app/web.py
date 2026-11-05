import os
import secrets
from typing import Mapping, Optional

from flask import Flask, render_template

from python_app.database import initialize_database
from python_app.routes.characters import characters
from python_app.routes.home import home
from python_app.routes.scores import scores
from python_app.routes.stats import stats


def create_app(config: Optional[Mapping[str, object]] = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE_URL=os.environ.get("DATABASE_URL", ""),
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
    )
    app.config.update(config or {})
    app.register_blueprint(home)
    app.register_blueprint(scores)
    app.register_blueprint(stats)
    app.register_blueprint(characters)
    return app


def main() -> None:
    app = create_app()
    initialize_database(app.config["DATABASE_URL"])
    app.run(host="0.0.0.0", port=5000)
