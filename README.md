# python-app

A Python application with a command-line greeting and a Flask landing page.

## Requirements

- Python 3.9 or newer

## Setup

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
python -m pip install -e ".[test]"
```

## Run

```sh
python-app
python-app Ada
```

## Run the web app

```sh
python-app-web
```

The scores page requires PostgreSQL. Docker Compose starts the app and its database together; use the local command only when a PostgreSQL server is already configured through `DATABASE_URL`.

The home page is at `/`, with the feature pages at `/scores` and `/personnages`.

## Run with Docker Compose

Build the image and start the web app from the repository root:

```sh
docker compose up --build
```

Then open <http://127.0.0.1:5001>. The pages are available at `/`, `/scores`, and `/personnages`. If that port is already in use, choose another host port, for example `APP_PORT=5058 docker compose up --build`. Stop the app with `Ctrl+C`, or run it in the background:

```sh
docker compose up --build -d
docker compose down
```

The scores page records each duel between exactly two players: date, duration in minutes, winner (or a draw), characters, and an optional comment for each player. PostgreSQL runs in its own container, and its data is persisted in the `villainous_data` Docker volume, even after `docker compose down`. Existing numeric results are migrated to wins, losses, or draws when the app starts. To permanently delete the saved duels, run `docker compose down -v`.

To run the CLI in the container instead:

```sh
docker compose run --rm --entrypoint python-app app Ada
```

## Test

```sh
python -m pytest
```
