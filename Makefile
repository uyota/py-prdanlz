export PYTHONPATH=src

PYTHON ?= python3

default : test

run :
	$(PYTHON) -m prdanlz --config prdanlz.json -l prdanlz.log -i 10

test :
	$(PYTHON) -m pytest
