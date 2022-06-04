# Development Tools

1. black formatter

## Development Dependency

### Ports

1. py-pytest
1. py-black / py-pytest-black
1. py-mock
1. py-coverage / py-pytest-cov
1. py-sqlit3 ?

### pip

Python on FreeBSD requires py-sqlite3 from pkg/ports even in venv.

``` csh
% python3.8 -m venv ../venv38
% source ../venv38/bin/activate.csh
% pip install -r requirements.txt
```
