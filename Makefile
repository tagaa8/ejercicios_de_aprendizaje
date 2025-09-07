PY := python3
PIP := pip
UVICORN := uvicorn

.PHONY: install run seed clean

install:
	$(PY) -m venv .venv
	. .venv/bin/activate && $(PIP) install -U pip
	. .venv/bin/activate && $(PIP) install -r backend/requirements.txt

run:
	. .venv/bin/activate && $(UVICORN) backend.app:app --reload --port 8000

seed:
	. .venv/bin/activate && $(PY) scripts/seed.py

clean:
	rm -rf .venv data/__pycache__ **/__pycache__
	rm -f data/app.db

