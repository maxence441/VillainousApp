from flask import Blueprint, render_template

scores = Blueprint("scores", __name__, url_prefix="/scores")


@scores.get("")
def index() -> str:
    return render_template("scores.html")
