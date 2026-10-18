.PHONY: up down test evals run-analyzer

up:
	docker compose up -d

down:
	docker compose down

test:
	python3 -m pytest -q

evals:
	python3 -m apps.stock_analyzer.cli --evals

run-analyzer:
	python3 -m apps.stock_analyzer.cli --sample
