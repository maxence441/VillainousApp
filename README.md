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

## Test

```sh
python -m pytest
```
