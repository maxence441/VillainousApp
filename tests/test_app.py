from python_app import greet


def test_greet_uses_the_supplied_name() -> None:
    assert greet("Ada") == "Hello, Ada!"


def test_greet_defaults_to_world() -> None:
    assert greet() == "Hello, world!"
