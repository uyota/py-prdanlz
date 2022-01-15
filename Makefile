export PYTHONPATH=src

PYTHON ?= python

# REPO = --repository testpypi
# PIPURL = --index-url https://test.pypi.org/simple/

default : test

run :
	$(PYTHON) -m prdanlz --config prdanlz.json -l prdanlz.log -i 10

debug :
	$(PYTHON) -m prdanlz --config prdanlz.json -l prdanlz.log -i 10 -d

test :
	$(PYTHON) -m pytest

build :
	$(PYTHON) -m build

upload :
	$(PYTHON) -m twine upload $(REPO) dist/*

pip-install :
	# $(PYTHON) -m pip install $(PIPURL) --no-deps prdanlz-uyota
	$(PYTHON) -m pip install $(PIPURL) prdanlz-uyota

clean :
	rm -rf build dist

.PHONY : run test build upload clean
