import argparse

from python_app import greet


def main() -> None:
    parser = argparse.ArgumentParser(description="A minimal greeting application")
    parser.add_argument("name", nargs="?", default="world", help="who to greet")
    args = parser.parse_args()
    print(greet(args.name))
