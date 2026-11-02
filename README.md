# python-app

A minimal Python command-line application packaged with a `src/` layout.

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

## Run with Docker

Build the image from the repository root:

```sh
docker build -t python-app .
```

Run the application with its default greeting or pass a name:

```sh
docker run --rm python-app
docker run --rm python-app Ada
```

## Test

```sh
python -m pytest
```
