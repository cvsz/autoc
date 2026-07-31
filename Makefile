PYTHON ?= python3
VENV_PYTHON := .venv/bin/python3
VENV_PIP := .venv/bin/pip
HOST ?= 0.0.0.0
PORT ?= 8000

.PHONY: build start clean

build:
	@if [ ! -x "$(VENV_PYTHON)" ]; then $(PYTHON) -m venv .venv; fi
	@$(VENV_PIP) install -e .
	@$(VENV_PYTHON) -m py_compile monitor_core.py app.py realtime_monitor.py gui.py tests/test_monitor_core.py tests/test_app.py
	@$(VENV_PYTHON) -m unittest discover -s tests -p 'test_*.py'

start:
	@if [ -x "$(VENV_PYTHON)" ]; then exec $(VENV_PYTHON) app.py --host $(HOST) --port $(PORT); else exec $(PYTHON) app.py --host $(HOST) --port $(PORT); fi

clean:
	@rm -rf .venv __pycache__ */__pycache__ .pytest_cache build dist *.egg-info
