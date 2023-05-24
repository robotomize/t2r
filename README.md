# t2r
Getting a list of relays to use in the tor browser.

## Install

Install Python3.9

```shell
python3 -m venv env
pip3 install poetry
poetry install --no-dev
python3 main.py
```

### Example
```shell
python3 --proxy 'http://8.8.8.8:8181,http:/9.9.9.9:9191' --timeout 3 --count 30 main.py
```

### Options

- timeout - request timeout
- count - number of relays
- proxy - list of proxies
