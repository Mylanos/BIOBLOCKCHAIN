VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
FILE_CLIENT = src/file_client.py

TEST_SCRIPT = tests/test_fileclient.py
DB_FILE = data/db.json
JSON_SERVER = node_modules/.bin/json-server

all: run

help: venv_
	$(PYTHON) $(FILE_CLIENT) -h


run: venv_
	$(PYTHON) $(FILE_CLIENT) stat $(DEFAULT_UUID)


test_:
	$(PYTHON) -m unittest discover


venv_:
	python3 -m venv .venv;
	$(PIP) install -r requirements.txt;

npm:
	npm install

req: venv_
	$(PIP) freeze > requirements.txt

clean:
	rm -rf .pytest_cache
	rm -rf src/__pycache__
	rm -rf test/__pycache__
	rm -rf $(VENV)
	rm -rf node_modules
	rm -rf source
	rm package-lock.json

runRead: venv_
	$(PYTHON) $(FILE_CLIENT) read $(DEFAULT_UUID)


server: npm
	$(JSON_SERVER) --watch $(DB_FILE)