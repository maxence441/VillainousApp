from flask import Blueprint, render_template

home = Blueprint("home", __name__)


@home.get("/")
def index() -> str:
    return render_template("index.html")
