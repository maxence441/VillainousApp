from flask import Blueprint, render_template

characters = Blueprint("characters", __name__, url_prefix="/personnages")


@characters.get("")
def index() -> str:
    return render_template("characters.html")
