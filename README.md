# t2r
cli app for fetching tor relays

## Usage

Python3.9

```shell
python3 -m venv env
pip3 install poetry
poetry install --no-dev
python3 main.py
```

### Options

timeout - request timeout

count - number of relays

proxy - list of proxies

```shell
python3 --proxy 'http://8.8.8.8:8181,http:/9.9.9.9:9191' --timeout 3 --count 30 main.py
```