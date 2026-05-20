COMPOSE ?= docker compose
REGISTRY ?= ghcr.io/eridanusq/nekocafe
TAG ?= 0.1.0

.PHONY: test build up down logs scan rollback

test:
	python -m unittest discover -s services/reservation/tests -v
	npm test --prefix services/member

build:
	docker build -t $(REGISTRY)/reservation:$(TAG) services/reservation
	docker build -t $(REGISTRY)/member:$(TAG) services/member

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f --tail=100

scan:
	trivy image --severity HIGH,CRITICAL --exit-code 1 $(REGISTRY)/reservation:$(TAG)
	trivy image --severity HIGH,CRITICAL --exit-code 1 $(REGISTRY)/member:$(TAG)

rollback:
	./scripts/rollback.sh staging
