from datetime import date

import pytest

from python_app import greet
from python_app.database import save_game
from python_app.web import create_app


def test_homepage_renders_three_dimensional_game_box_and_navigation() -> None:
    response = create_app().test_client().get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "VILLAINOUS" in page
    assert 'class="game-box"' in page
    assert "Scores" in page
    assert "Personnages" in page
    assert 'href="/scores"' in page
    assert 'href="/personnages"' in page


def test_scores_route_displays_game_entry_form(monkeypatch) -> None:
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [])
    response = create_app({"DATABASE_URL": "postgresql://test"}).test_client().get(
        "/scores"
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Enregistrer un duel" in page
    assert 'name="player_name"' in page
    assert 'name="character"' in page
    assert 'name="duration_minutes"' in page
    assert 'name="comment"' in page
    assert 'name="winner"' in page
    assert page.count('name="player_name"') == 2
    assert "Maléfique" in page
    assert 'aria-current="page"' in response.get_data(as_text=True)


def test_scores_route_saves_duel_winner_duration_and_comments(monkeypatch) -> None:
    saved_games = []
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [])
    monkeypatch.setattr(
        "python_app.routes.scores.save_game",
        lambda database_url, played_on, duration_minutes, players: saved_games.append(
            (database_url, played_on, duration_minutes, players)
        ),
    )
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post(
        "/scores",
        data={
            "played_on": "2026-11-02",
            "duration_minutes": "75",
            "player_name": ["Alice", "Bob"],
            "character": ["Maléfique", "Jafar"],
            "comment": ["Belle stratégie", "Presque !"],
            "winner": "player1",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/scores")
    assert saved_games == [
        (
            "postgresql://test",
            date(2026, 11, 2),
            75,
            [
                {
                    "name": "Alice",
                    "character": "Maléfique",
                    "result": "win",
                    "comment": "Belle stratégie",
                },
                {
                    "name": "Bob",
                    "character": "Jafar",
                    "result": "loss",
                    "comment": "Presque !",
                },
            ],
        )
    ]


def test_scores_route_saves_a_draw(monkeypatch) -> None:
    saved_games = []
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [])
    monkeypatch.setattr(
        "python_app.routes.scores.save_game",
        lambda database_url, played_on, duration_minutes, players: saved_games.append(
            players
        ),
    )
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post(
        "/scores",
        data={
            "played_on": "2026-11-02",
            "duration_minutes": "60",
            "player_name": ["Alice", "Bob"],
            "character": ["Maléfique", "Jafar"],
            "comment": ["", ""],
            "winner": "draw",
        },
    )

    assert response.status_code == 302
    assert saved_games == [
        [
            {"name": "Alice", "character": "Maléfique", "result": "draw", "comment": ""},
            {"name": "Bob", "character": "Jafar", "result": "draw", "comment": ""},
        ]
    ]


def test_scores_route_displays_duel_duration_and_comments(monkeypatch) -> None:
    monkeypatch.setattr(
        "python_app.routes.scores.list_games",
        lambda database_url: [
            {
                "id": 3,
                "played_on": date(2026, 11, 2),
                "duration_minutes": 45,
                "players": [
                    {
                        "name": "Alice",
                        "character": "Maléfique",
                        "result": "win",
                        "comment": "Victoire mémorable",
                    },
                    {
                        "name": "Bob",
                        "character": "Jafar",
                        "result": "loss",
                        "comment": "",
                    },
                ],
            }
        ],
    )

    response = create_app({"DATABASE_URL": "postgresql://test"}).test_client().get(
        "/scores"
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "45 min" in page
    assert "Victoire" in page
    assert "Défaite" in page
    assert "Victoire mémorable" in page


def test_scores_route_opens_prefilled_edit_form(monkeypatch) -> None:
    game = {
        "id": 12,
        "played_on": date(2026, 11, 2),
        "duration_minutes": 45,
        "winner": "player2",
        "players": [
            {
                "name": "Alice",
                "character": "Maléfique",
                "result": "loss",
                "comment": "À améliorer",
            },
            {
                "name": "Bob",
                "character": "Jafar",
                "result": "win",
                "comment": "Bien joué",
            },
        ],
    }
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [game])
    monkeypatch.setattr("python_app.routes.scores.get_game", lambda database_url, game_id: game)
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.get("/scores/12/edit")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'action="/scores/12/edit"' in page
    assert 'value="Alice"' in page
    assert 'value="45"' in page
    assert "À améliorer" in page
    assert '<option value="player2" selected>' in page
    assert 'aria-label="Supprimer le duel 12"' in page


def test_scores_route_updates_only_the_selected_duel(monkeypatch) -> None:
    game = {
        "id": 12,
        "played_on": date(2026, 11, 2),
        "duration_minutes": 45,
        "winner": "player2",
        "players": [],
    }
    updated_games = []
    monkeypatch.setattr("python_app.routes.scores.get_game", lambda database_url, game_id: game)
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [game])
    monkeypatch.setattr(
        "python_app.routes.scores.update_game",
        lambda database_url, game_id, played_on, duration_minutes, players: (
            updated_games.append((game_id, played_on, duration_minutes, players)) or True
        ),
    )
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post(
        "/scores/12/edit",
        data={
            "played_on": "2026-11-03",
            "duration_minutes": "70",
            "player_name": ["Alice", "Bob"],
            "character": ["Maléfique", "Jafar"],
            "comment": ["", "Revanche"],
            "winner": "draw",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/scores")
    assert updated_games == [
        (
            12,
            date(2026, 11, 3),
            70,
            [
                {
                    "name": "Alice",
                    "character": "Maléfique",
                    "result": "draw",
                    "comment": "",
                },
                {
                    "name": "Bob",
                    "character": "Jafar",
                    "result": "draw",
                    "comment": "Revanche",
                },
            ],
        )
    ]


def test_scores_route_rejects_edit_for_unknown_duel(monkeypatch) -> None:
    monkeypatch.setattr("python_app.routes.scores.get_game", lambda database_url, game_id: None)
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    assert client.get("/scores/404/edit").status_code == 404
    assert client.post("/scores/404/edit").status_code == 404


def test_scores_route_deletes_selected_duel(monkeypatch) -> None:
    deleted = []
    monkeypatch.setattr(
        "python_app.routes.scores.delete_game",
        lambda database_url, game_id: deleted.append(game_id) or True,
    )
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post("/scores/12/delete")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/scores")
    assert deleted == [12]


def test_scores_route_returns_404_when_duel_to_delete_does_not_exist(monkeypatch) -> None:
    monkeypatch.setattr(
        "python_app.routes.scores.delete_game",
        lambda database_url, game_id: False,
    )
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    assert client.post("/scores/404/delete").status_code == 404


def test_save_game_rejects_non_duels_before_connecting() -> None:
    with pytest.raises(ValueError, match="exactly two players"):
        save_game("postgresql://unused", date.today(), 45, [])


def test_save_game_rejects_inconsistent_duel_results_before_connecting() -> None:
    players = [
        {"result": "win"},
        {"result": "win"},
    ]

    with pytest.raises(ValueError, match="one winner and one loser"):
        save_game("postgresql://unused", date.today(), 45, players)


def test_scores_route_rejects_games_with_one_player(monkeypatch) -> None:
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [])
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post(
        "/scores",
        data={
            "played_on": "2026-11-02",
            "duration_minutes": "60",
            "player_name": ["Alice"],
            "character": ["Maléfique"],
            "comment": [""],
            "winner": "player1",
        },
    )

    assert response.status_code == 400
    assert "exactement deux joueurs" in response.get_data(as_text=True)


def test_scores_route_rejects_invalid_duration(monkeypatch) -> None:
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [])
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post(
        "/scores",
        data={
            "played_on": "2026-11-02",
            "duration_minutes": "0",
            "player_name": ["Alice", "Bob"],
            "character": ["Maléfique", "Jafar"],
            "comment": ["", ""],
            "winner": "player1",
        },
    )

    assert response.status_code == 400
    assert "durée doit être comprise" in response.get_data(as_text=True)


def test_characters_route_is_served_by_its_blueprint() -> None:
    response = create_app().test_client().get("/personnages")

    assert response.status_code == 200
    assert "galerie des personnages" in response.get_data(as_text=True)
    assert 'aria-current="page"' in response.get_data(as_text=True)


def test_homepage_stylesheet_has_box_animation() -> None:
    response = create_app().test_client().get("/static/villainous.css")

    assert response.status_code == 200
    assert "box-float" in response.get_data(as_text=True)


def test_greet_uses_the_supplied_name() -> None:
    assert greet("Ada") == "Hello, Ada!"


def test_greet_defaults_to_world() -> None:
    assert greet() == "Hello, world!"
