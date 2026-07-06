.PHONY: test evals demo serve lint

test:
	python -m pytest tests/ -v

evals:
	python evals/run_all.py

demo:
	bash demo/demo_10min.sh

serve:
	uvicorn app.main:app --host 0.0.0.0 --port 7020 --reload

lint:
	python -m ruff check app/ tests/
