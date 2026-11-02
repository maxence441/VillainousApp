from flask import Flask, render_template


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def home() -> str:
        return render_template("index.html")

    return app


def main() -> None:
    create_app().run(host="0.0.0.0", port=5000)
