from datetime import date
from typing import Any, Optional

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from python_app.database import delete_game, get_game, list_games, save_game, update_game

scores = Blueprint("scores", __name__, url_prefix="/scores")

CHARACTERS = (
    "Maléfique",
    "Jafar",
    "Ursula",
    "Capitaine Crochet",
    "Prince Jean",
    "Reine de Cœur",
    "La Méchante Reine",
    "Hadès",
    "Docteur Facilier",
    "Scar",
    "Yzma",
    "Ratigan",
    "Cruella d’Enfer",
    "Pat Hibulaire",
    "Mère Gothel",
    "Gaston",
    "Lady Trémaine",
    "Le Seigneur des Ténèbres",
    "Oogie Boogie",
    "Chernabog",
    "Roi Candy",
    "Syndrome",
    "Lotso",
    "Madame Mim",
    "Davy Jones",
    "Tamatoa",
    "Sœurs Sanderson",
)

DEFAULT_PLAYERS = [
    {"name": "", "character": "", "comment": ""},
    {"name": "", "character": "", "comment": ""},
]


def _render_scores(
    *,
    status: int = 200,
    players: Optional[list[dict[str, Any]]] = None,
    errors: Optional[list[str]] = None,
    played_on: Optional[str] = None,
    duration_minutes: Optional[str] = None,
    winner: Optional[str] = None,
    edit_game_id: Optional[int] = None,
    edit_values: Optional[dict[str, Any]] = None,
) -> tuple[str, int]:
    games = list_games(current_app.config["DATABASE_URL"])
    return (
        render_template(
            "scores.html",
            characters=CHARACTERS,
            errors=errors or [],
            games=games,
            played_on=played_on or date.today().isoformat(),
            duration_minutes=duration_minutes or "",
            players=players or DEFAULT_PLAYERS,
            winner=winner or "",
            edit_game_id=edit_game_id,
            edit_values=edit_values,
        ),
        status,
    )


def _parse_duel_form() -> tuple[Optional[dict[str, Any]], list[str], dict[str, Any]]:
    names = request.form.getlist("player_name")
    characters = request.form.getlist("character")
    comments = request.form.getlist("comment")
    raw_date = request.form.get("played_on", "")
    raw_duration = request.form.get("duration_minutes", "")
    winner = request.form.get("winner", "")
    rows = [
        {"name": name.strip(), "character": character, "comment": comment.strip()}
        for name, character, comment in zip(names, characters, comments)
    ]
    errors: list[str] = []

    if len(names) != 2 or len(characters) != 2 or len(comments) != 2:
        errors.append("Un duel doit réunir exactement deux joueurs.")

    try:
        played_on = date.fromisoformat(raw_date)
    except ValueError:
        played_on = date.today()
        errors.append("Choisissez une date de partie valide.")

    try:
        duration_minutes = int(raw_duration)
        if not 1 <= duration_minutes <= 1440:
            raise ValueError
    except ValueError:
        duration_minutes = 0
        errors.append("La durée doit être comprise entre 1 et 1 440 minutes.")

    if winner not in {"player1", "player2", "draw"}:
        errors.append("Choisissez le vainqueur du duel ou indiquez une égalité.")

    rows = (rows + DEFAULT_PLAYERS)[:2]
    for index, row in enumerate(rows, start=1):
        if not row["name"]:
            errors.append(f"Le nom du joueur {index} est obligatoire.")
        if len(row["name"]) > 80:
            errors.append(f"Le nom du joueur {index} ne peut pas dépasser 80 caractères.")
        if row["character"] not in CHARACTERS:
            errors.append(f"Choisissez un personnage valide pour le joueur {index}.")
        if len(row["comment"]) > 1000:
            errors.append(
                f"Le commentaire du joueur {index} ne peut pas dépasser 1 000 caractères."
            )

    form_values = {
        "played_on": raw_date,
        "duration_minutes": raw_duration,
        "players": rows,
        "winner": winner,
    }
    if errors:
        return None, errors, form_values

    results = {
        "player1": ["win", "loss"],
        "player2": ["loss", "win"],
        "draw": ["draw", "draw"],
    }[winner]
    return (
        {
            "played_on": played_on,
            "duration_minutes": duration_minutes,
            "players": [
                {
                    "name": row["name"],
                    "character": row["character"],
                    "result": results[index],
                    "comment": row["comment"],
                }
                for index, row in enumerate(rows)
            ],
        },
        [],
        form_values,
    )


@scores.get("")
def index() -> tuple[str, int]:
    return _render_scores()


@scores.post("")
def create() -> Any:
    duel, errors, form_values = _parse_duel_form()
    if errors:
        return _render_scores(
            status=400,
            errors=errors,
            players=form_values["players"],
            played_on=form_values["played_on"],
            duration_minutes=form_values["duration_minutes"],
            winner=form_values["winner"],
        )

    save_game(
        current_app.config["DATABASE_URL"],
        duel["played_on"],
        duel["duration_minutes"],
        duel["players"],
    )
    flash("Le duel a été enregistré.", "success")
    return redirect(url_for("scores.index"))


@scores.get("/<int:game_id>/edit")
def edit(game_id: int) -> tuple[str, int]:
    game = get_game(current_app.config["DATABASE_URL"], game_id)
    if game is None:
        abort(404)
    edit_values = {
        "played_on": game["played_on"].isoformat(),
        "duration_minutes": (
            str(game["duration_minutes"]) if game["duration_minutes"] is not None else ""
        ),
        "players": game["players"],
        "winner": game["winner"],
    }
    return _render_scores(edit_game_id=game_id, edit_values=edit_values)


@scores.post("/<int:game_id>/edit")
def update(game_id: int) -> Any:
    if get_game(current_app.config["DATABASE_URL"], game_id) is None:
        abort(404)

    duel, errors, form_values = _parse_duel_form()
    if errors:
        return _render_scores(
            status=400,
            errors=errors,
            edit_game_id=game_id,
            edit_values=form_values,
        )

    if not update_game(
        current_app.config["DATABASE_URL"],
        game_id,
        duel["played_on"],
        duel["duration_minutes"],
        duel["players"],
    ):
        abort(404)
    flash("Le duel a été modifié.", "success")
    return redirect(url_for("scores.index"))


@scores.post("/<int:game_id>/delete")
def remove(game_id: int) -> Any:
    if not delete_game(current_app.config["DATABASE_URL"], game_id):
        abort(404)
    flash("Le duel a été supprimé.", "success")
    return redirect(url_for("scores.index"))
