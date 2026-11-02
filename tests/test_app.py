from python_app import greet
from python_app.web import create_app


def test_homepage_renders_three_dimensional_game_box_and_navigation() -> None:
    response = create_app().test_client().get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "VILLAINOUS" in page
    assert 'class="game-box"' in page
    assert "Scores" in page
    assert "Lanceur" in page


def test_homepage_stylesheet_has_box_animation() -> None:
    response = create_app().test_client().get("/static/villainous.css")

    assert response.status_code == 200
    assert "box-float" in response.get_data(as_text=True)


def test_greet_uses_the_supplied_name() -> None:
    assert greet("Ada") == "Hello, Ada!"


def test_greet_defaults_to_world() -> None:
    assert greet() == "Hello, world!"
