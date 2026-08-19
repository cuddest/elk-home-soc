.PHONY: init up down reset status smoke test detect views

init:
	cp -n .env.example .env || true
	./scripts/bootstrap-certs.sh

up:
	docker compose up -d

down:
	docker compose down

reset:
	./scripts/reset-lab.sh

status:
	./scripts/status.sh

smoke:
	./scripts/smoke-test.sh

test:
	python3 -m pytest -q

detect:
	python3 scripts/detect.py --once

views:
	python3 scripts/create-kibana-data-views.py
