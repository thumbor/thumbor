# NSXBet targets — local run and API smoke tests.
# Included from Makefile; upstream targets untouched.

PROJECT_NAME := nsx-thumbor
COMPOSE := docker compose -f docker/docker-compose.nsx.yaml -p $(PROJECT_NAME)

.PHONY: run run-bg stop logs test-api docker-build

##@ Run

run: docker-build ## Run full local stack (thumbor + statsd + prometheus + grafana)
	$(COMPOSE) up --remove-orphans

run-bg: docker-build ## Run stack in background
	$(COMPOSE) up -d --remove-orphans
	@echo "thumbor: http://localhost:8888  grafana: http://localhost:3000 (admin/admin)  prometheus: http://localhost:9090"

stop: ## Stop the stack
	$(COMPOSE) down -v

logs: ## Tail stack logs
	$(COMPOSE) logs -f thumbor

##@ Build

docker-build: ## Build the thumbor image
	$(COMPOSE) build thumbor

##@ Test

test-api: ## Smoke-test the running API (run `make run-bg` first)
	bash scripts/test-api.sh
