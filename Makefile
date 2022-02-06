export PYTHONPATH=src

PYTHON ?= python

# REPO = --repository testpypi
# PIPURL = --index-url https://test.pypi.org/simple/

PRDANLZ ?= $(PYTHON) -m prdanlz -l prdanlz.log -i $(INTERVAL)
INTERVAL ?= 10

default : test

run :
	$(PYTHON) -m prdanlz --config prdanlz.json -l prdanlz.log -i 10

debug :
	$(PYTHON) -m prdanlz --config prdanlz.json -l prdanlz.log -i 10 -d

test :
	$(PYTHON) -m pytest --cov=src

coverage :
	coverage report -m

coverage-html :
	coverage html

build :
	$(PYTHON) -m build

upload :
	ls -l dist
	$(PYTHON) -m twine upload $(REPO) dist/*

pip-install :
	# $(PYTHON) -m pip install $(PIPURL) --no-deps prdanlz-uyota
	$(PYTHON) -m pip install $(PIPURL) prdanlz-uyota

clean :
	rm -rf build dist .coverage htmlcov `find . -name __pycache__`

.PHONY : run debug test build coverage coverage-html upload pip-install clean


cpu_load :
	$(PRDANLZ) --config examples/cpu_load.json
swap_usage :
	$(PRDANLZ) --config examples/swap_usage.json
battery :
	$(PRDANLZ) --config examples/battery.json
