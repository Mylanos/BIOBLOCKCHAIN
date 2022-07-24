VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
MAIN = bioblockchain.main

all: run

#TODO help description
help:
	$(PYTHON) -m $(MAIN) -h

#run script
run:
	$(PYTHON) -m $(MAIN)

# tests
tests:
	$(PYTHON) -m unittest discover

#this will install all requirements in venv, still MAKE SURE TO ACTIVATE VENV from your shell/terminal
install:
	( \
       source $(VENV)/bin/activate; \
       pip install -r requirements.txt; \
    )

clean:
	rm -rf .pytest_cache
	rm -rf bioblockchain/__pycache__
	rm -rf test/__pycache__
	rm -rf $(VENV)
