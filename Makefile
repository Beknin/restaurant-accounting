IMAGE_NAME = restaurant-app
IMAGE_TAG = latest
CONTAINER_HR = restaurant-hr
CONTAINER_EMP = restaurant-emp
DB_DIR = infra/db
DOCKER_COMPOSE = docker compose

.PHONY: help
help:
	@echo "Docker:"
	@echo "  make hr                    Run HR panel"
	@echo "  make emp ID=5              Run employee panel"
	@echo ""
	@echo "Local:"
	@echo "  make local-hr              Run HR locally"
	@echo "  make local-emp ID=5        Run employee locally"
	@echo "  make local-login           Run with login screen"
	@echo ""
	@echo "Manage:"
	@echo "  make stop-hr               Stop HR"
	@echo "  make stop-emp ID=5         Stop employee"
	@echo "  make stop-all              Stop all"
	@echo "  make clean-db              Delete database"
	@echo ""
	@echo "Setup:"
	@echo "  make install               Install dependencies"
	@echo "  make build                 Build image"
	@echo "  make setup                 Full setup"

.PHONY: build
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: install
install:
	poetry install --only main

.PHONY: setup
setup: build install
	mkdir -p $(DB_DIR)

.PHONY: hr
hr:
	$(DOCKER_COMPOSE) run --rm hr-panel

.PHONY: emp
emp:
	@test -n "$(ID)" || (echo "Error: make emp ID=5"; exit 1)
	EMPLOYEE_ID=$(ID) $(DOCKER_COMPOSE) --profile employee run --rm employee-panel

.PHONY: local-hr
local-hr: install
	ROLE=hr python3 app/ui/main.py

.PHONY: local-emp
local-emp: install
	@test -n "$(ID)" || (echo "Error: make local-emp ID=5"; exit 1)
	ROLE=employee EMPLOYEE_ID=$(ID) python3 app/ui/main.py

.PHONY: local-login
local-login: install
	python3 app/ui/main.py

.PHONY: stop-hr
stop-hr:
	-docker stop $(CONTAINER_HR)

.PHONY: stop-emp
stop-emp:
	@test -n "$(ID)" || (echo "Error: make stop-emp ID=5"; exit 1)
	-docker stop $(CONTAINER_EMP)-$(ID)

.PHONY: stop-all
stop-all:
	-docker stop $(CONTAINER_HR) $(CONTAINER_EMP)-* 2>/dev/null

.PHONY: clean-db
clean-db:
	rm -f $(DB_DIR)/database.db