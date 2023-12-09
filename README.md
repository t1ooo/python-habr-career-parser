Habr Career Parser

Setup

Install [poetry](https://python-poetry.org/) if it is not already installed.

Install project dependencies
```sh
poetry install
```

Run tests
```sh
poetry run pytest
```

Parse some data
```sh
./main.sh --page 1 --save data.csv
```

Display help information
```sh
./main.sh --help
```

Tags: python, habr, parser, xml, httpx