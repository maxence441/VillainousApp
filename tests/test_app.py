from datetime import date

import pytest

from python_app import greet
from python_app.database import save_game
from python_app.routes.characters import VILLAIN_CARDS
from python_app.routes.scores import CHARACTERS
from python_app.routes.stats import _build_statistics
from python_app.web import create_app


def test_homepage_renders_three_dimensional_game_box_and_navigation() -> None:
    response = create_app().test_client().get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "VILLAINOUS" in page
    assert 'class="game-box"' in page
    assert "Scores" in page
    assert "Stats" in page
    assert "Personnages" in page
    assert 'href="/scores"' in page
    assert 'href="/stats"' in page
    assert 'href="/personnages"' in page
    assert 'href="/static/villainous.css"' in page
    assert 'href="/static/home.css"' in page
    assert 'href="/static/scores.css"' not in page


def test_stats_route_summarizes_recorded_games(monkeypatch) -> None:
    games = [
        {
            "id": 3,
            "played_on": date(2026, 11, 3),
            "duration_minutes": 60,
            "players": [
                {"name": "Alice", "character": "Maléfique", "result": "win"},
                {"name": "Bob", "character": "Jafar", "result": "loss"},
            ],
        },
        {
            "id": 2,
            "played_on": date(2026, 11, 2),
            "duration_minutes": 90,
            "players": [
                {"name": "Alice", "character": "Jafar", "result": "draw"},
                {"name": "Bob", "character": "Maléfique", "result": "draw"},
            ],
        },
        {
            "id": 1,
            "played_on": date(2026, 10, 31),
            "duration_minutes": 30,
            "players": [
                {"name": "Alice", "character": "Maléfique", "result": "win"},
                {"name": "Chloé", "character": "Ursula", "result": "loss"},
            ],
        },
    ]
    monkeypatch.setattr("python_app.routes.stats.list_games", lambda database_url: games)
    stats = _build_statistics(games)

    response = create_app({"DATABASE_URL": "postgresql://test"}).test_client().get(
        "/stats"
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Statistiques" in page
    assert "DUELS ARCHIVÉS" in page
    assert ">3<" in page
    assert "JOUEURS FIXES" not in page
    assert "ÉGALITÉS" in page
    assert "ÉCART AU SCORE" in page
    assert ">90 min<" in page
    assert "Maléfique" in page
    assert "Claire" in page
    assert "Maxence" in page
    assert "Alice" not in page
    assert "Face-à-face" in page
    assert "Personnage favori" in page
    assert "Taux d’égalité" in page
    assert "Parties nulles" in page
    assert "Novembre 2026" in page
    assert 'href="/static/stats.css"' in page
    assert 'aria-current="page"' in page
    assert stats["draws"] == 1
    assert stats["draw_rate"] == 33
    assert stats["decisive_games"] == 2
    assert stats["leader"] == "Claire"
    assert stats["win_margin"] == 2
    assert stats["average_draw_duration"] == 90
    assert stats["average_decisive_duration"] == 45
    assert stats["top_draw_character_pairings"] == [
        {"names": ("Jafar", "Maléfique"), "games": 1}
    ]


def test_stats_route_shows_empty_state_without_games(monkeypatch) -> None:
    monkeypatch.setattr("python_app.routes.stats.list_games", lambda database_url: [])

    response = create_app({"DATABASE_URL": "postgresql://test"}).test_client().get(
        "/stats"
    )
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Les chroniques sont encore vierges." in page
    assert 'href="/scores"' in page


def test_scores_route_displays_game_entry_form(monkeypatch) -> None:
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [])
    response = create_app({"DATABASE_URL": "postgresql://test"}).test_client().get(
        "/scores"
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Enregistrer un duel" in page
    assert 'href="/static/villainous.css"' in page
    assert 'href="/static/scores.css"' in page
    assert 'href="/static/home.css"' not in page
    assert "Claire" in page
    assert "Maxence" in page
    assert "Nom du joueur" not in page
    assert page.count('class="character-picker-toggle"') == 2
    assert page.count('class="character-filter" type="search"') == 2
    assert page.count('class="character-picker-option" type="button" role="option"') == 54
    assert 'name="character"' in page
    assert "<datalist" not in page
    assert '<option value="Maléfique">' in page
    assert 'name="duration_minutes"' in page
    assert 'name="comment"' in page
    assert 'name="winner"' in page
    assert 'name="player_name"' not in page
    assert "Claire gagne" in page
    assert "Maxence gagne" in page
    assert "Maléfique" in page
    assert 'aria-current="page"' in response.get_data(as_text=True)


def test_scores_route_paginates_games_three_per_page(monkeypatch) -> None:
    games = [
        {
            "id": game_id,
            "played_on": date(2026, 11, 2),
            "duration_minutes": 45,
            "players": [],
        }
        for game_id in range(12, 0, -1)
    ]
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: games)
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    first_page = client.get("/scores")
    second_page = client.get("/scores?page=2")
    last_page = client.get("/scores?page=99")

    assert first_page.status_code == 200
    first_page_html = first_page.get_data(as_text=True)
    assert first_page_html.count('class="game-card"') == 3
    assert "DUEL N° 012" in first_page_html
    assert "DUEL N° 010" in first_page_html
    assert "DUEL N° 009" not in first_page_html
    assert 'href="/scores?page=2#history-title"' in first_page_html
    assert 'loadScoresPage(link.href, true, targetId)' in first_page_html
    assert 'target.scrollIntoView' in first_page_html

    second_page_html = second_page.get_data(as_text=True)
    assert second_page_html.count('class="game-card"') == 3
    assert "DUEL N° 009" in second_page_html
    assert "DUEL N° 007" in second_page_html
    assert "DUEL N° 010" not in second_page_html
    assert 'aria-current="page">2</span>' in second_page_html

    last_page_html = last_page.get_data(as_text=True)
    assert last_page_html.count('class="game-card"') == 3
    assert "DUEL N° 001" in last_page_html
    assert "DUEL N° 003" in last_page_html
    assert "DUEL N° 004" not in last_page_html


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
                    "name": "Claire",
                    "character": "Maléfique",
                    "result": "win",
                    "comment": "Belle stratégie",
                },
                {
                    "name": "Maxence",
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
            "character": ["Maléfique", "Jafar"],
            "comment": ["", ""],
            "winner": "draw",
        },
    )

    assert response.status_code == 302
    assert saved_games == [
        [
            {"name": "Claire", "character": "Maléfique", "result": "draw", "comment": ""},
            {"name": "Maxence", "character": "Jafar", "result": "draw", "comment": ""},
        ]
    ]


def test_scores_route_rejects_the_same_character_for_both_players(monkeypatch) -> None:
    saved_games = []
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [])
    monkeypatch.setattr(
        "python_app.routes.scores.save_game",
        lambda *args: saved_games.append(args),
    )
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post(
        "/scores",
        data={
            "played_on": "2026-11-02",
            "duration_minutes": "60",
            "character": ["Maléfique", "Maléfique"],
            "comment": ["", ""],
            "winner": "player1",
        },
    )

    assert response.status_code == 400
    assert "Les deux joueurs doivent choisir des personnages différents." in (
        response.get_data(as_text=True)
    )
    assert saved_games == []


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
    assert "Claire" in page
    assert "Maxence" in page
    assert "Alice" not in page
    assert 'class="winner-row"' in page
    assert 'class="loss-row"' in page
    assert 'class="result-badge result-win"' in page
    assert 'class="result-badge result-loss"' in page
    assert 'data-tooltip="Modifier ce duel"' in page
    assert 'data-tooltip="Supprimer ce duel"' in page
    assert 'href="/scores/3/edit#game-card-3"' in page
    assert 'action="/scores/3/delete?page=1"' in page


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
    assert 'id="game-card-12"' in page
    assert 'data-tooltip="Annuler la modification"' in page
    assert 'action="/scores/12/edit"' in page
    assert "Claire" in page
    assert "Maxence" in page
    assert "Alice" not in page
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
                    "name": "Claire",
                    "character": "Maléfique",
                    "result": "draw",
                    "comment": "",
                },
                {
                    "name": "Maxence",
                    "character": "Jafar",
                    "result": "draw",
                    "comment": "Revanche",
                },
            ],
        )
    ]


def test_scores_route_rejects_duplicate_characters_when_updating_a_duel(monkeypatch) -> None:
    game = {
        "id": 12,
        "played_on": date(2026, 11, 2),
        "duration_minutes": 45,
        "players": [],
    }
    updated_games = []
    monkeypatch.setattr("python_app.routes.scores.get_game", lambda database_url, game_id: game)
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [game])
    monkeypatch.setattr(
        "python_app.routes.scores.update_game",
        lambda *args: updated_games.append(args) or True,
    )
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post(
        "/scores/12/edit",
        data={
            "played_on": "2026-11-03",
            "duration_minutes": "70",
            "character": ["Jafar", "Jafar"],
            "comment": ["", ""],
            "winner": "player1",
        },
    )

    assert response.status_code == 400
    assert "Les deux joueurs doivent choisir des personnages différents." in (
        response.get_data(as_text=True)
    )
    assert updated_games == []


def test_scores_route_rejects_edit_for_unknown_duel(monkeypatch) -> None:
    monkeypatch.setattr("python_app.routes.scores.get_game", lambda database_url, game_id: None)
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    assert client.get("/scores/404/edit").status_code == 404
    assert client.post("/scores/404/edit").status_code == 404


def test_scores_route_deletes_selected_duel(monkeypatch) -> None:
    deleted = []
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [])
    monkeypatch.setattr(
        "python_app.routes.scores.delete_game",
        lambda database_url, game_id: deleted.append(game_id) or True,
    )
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post("/scores/12/delete")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/scores#history-title")
    assert deleted == [12]


def test_scores_route_keeps_valid_page_after_deleting_duel(monkeypatch) -> None:
    remaining_games = [{"id": game_id} for game_id in range(5)]
    monkeypatch.setattr(
        "python_app.routes.scores.delete_game",
        lambda database_url, game_id: True,
    )
    monkeypatch.setattr(
        "python_app.routes.scores.list_games",
        lambda database_url: remaining_games,
    )
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post("/scores/12/delete?page=3")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/scores?page=2#history-title")


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
            "character": ["Maléfique", "Jafar"],
            "comment": ["", ""],
            "winner": "player1",
        },
    )

    assert response.status_code == 400
    assert "durée doit être comprise" in response.get_data(as_text=True)


def test_scores_route_rejects_character_outside_the_list(monkeypatch) -> None:
    monkeypatch.setattr("python_app.routes.scores.list_games", lambda database_url: [])
    client = create_app({"DATABASE_URL": "postgresql://test"}).test_client()

    response = client.post(
        "/scores",
        data={
            "played_on": "2026-11-02",
            "duration_minutes": "60",
            "character": ["Maléfique", "Personnage inventé"],
            "comment": ["", ""],
            "winner": "player1",
        },
    )

    assert response.status_code == 400
    assert "Choisissez un personnage valide pour le joueur 2." in response.get_data(
        as_text=True
    )


def test_characters_route_is_served_by_its_blueprint() -> None:
    response = create_app().test_client().get("/personnages")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Les <em>Personnages.</em>" in page
    assert page.count('class="villain-card"') == len(CHARACTERS)
    assert page.count("<details class=\"villain-card\"") == len(CHARACTERS)
    assert page.count('class="villain-details"') == len(CHARACTERS)
    assert 'class="villain-sigil"' not in page
    assert len(VILLAIN_CARDS) == len(CHARACTERS)
    assert {villain["name"] for villain in VILLAIN_CARDS} == set(CHARACTERS)
    assert "APPROCHE DE JEU" in page
    assert "Axes de jeu" in page
    assert "Maléfique" in page
    assert "Sœurs Sanderson" in page
    assert "FONCTIONNALITÉ EN PRÉPARATION" not in page
    assert "Catalogue officiel Ravensburger" in page
    assert "Développer la fiche" in page
    assert "Lecture stratégique" in page
    assert "Conseil de pilotage" in page
    assert all(villain["advice"] in page for villain in VILLAIN_CARDS)
    assert "Objectif, cartes et plateau" in page
    assert "notice de la boîte correspondante" in page
    assert "character-search" in page
    assert 'aria-current="page"' in page
    assert 'href="/static/villainous.css"' in page
    assert 'href="/static/characters.css"' in page
    assert 'href="/static/home.css"' not in page
    assert 'href="/static/scores.css"' not in page


def test_homepage_stylesheet_has_box_animation() -> None:
    client = create_app().test_client()
    common = client.get("/static/villainous.css")
    home = client.get("/static/home.css")
    scores = client.get("/static/scores.css")
    characters = client.get("/static/characters.css")

    assert (
        common.status_code
        == home.status_code
        == scores.status_code
        == characters.status_code
        == 200
    )
    common_css = common.get_data(as_text=True)
    home_css = home.get_data(as_text=True)
    scores_css = scores.get_data(as_text=True)
    characters_css = characters.get_data(as_text=True)
    assert "--gold:" in common_css
    assert ".nav-button" in common_css
    assert ".feature-page" in common_css
    assert ".hero {" not in common_css
    assert ".scores-page {" not in common_css
    assert ".hero {" in home_css
    assert "box-float" in home_css
    assert ".scores-page {" not in home_css
    assert ".scores-page {" in scores_css
    assert ".game-card {" in scores_css
    assert ".hero {" not in scores_css
    assert ".character-catalog {" in characters_css
    assert "align-items: start;" in characters_css
    assert ".villain-card {" in characters_css


def test_greet_uses_the_supplied_name() -> None:
    assert greet("Ada") == "Hello, Ada!"


def test_greet_defaults_to_world() -> None:
    assert greet() == "Hello, world!"
