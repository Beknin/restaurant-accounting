IMAGE_NAME = restaurant-app
IMAGE_TAG = latest
CONTAINER_HR = restaurant-hr
CONTAINER_EMP = restaurant-emp
DB_DIR = infra/db
DOCKER_COMPOSE = docker compose

.PHONY: help hr emp local-hr local-emp local-login stop-hr stop-emp stop-all clean-db install build setup

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

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

install:
	poetry install --only main

setup: build install
	mkdir -p $(DB_DIR)

hr:
	$(DOCKER_COMPOSE) run --rm hr-panel

emp:
	@test -n "$(ID)" || (echo "Error: make emp ID=5"; exit 1)
	EMPLOYEE_ID=$(ID) $(DOCKER_COMPOSE) --profile employee run --rm employee-panel

local-hr: install
	ROLE=hr python3 app/ui/main.py

local-emp: install
	@test -n "$(ID)" || (echo "Error: make local-emp ID=5"; exit 1)
	ROLE=employee EMPLOYEE_ID=$(ID) python3 app/ui/main.py

local-login: install
	python3 app/ui/main.py

stop-hr:
	-docker stop $(CONTAINER_HR)

stop-emp:
	@test -n "$(ID)" || (echo "Error: make stop-emp ID=5"; exit 1)
	-docker stop $(CONTAINER_EMP)-$(ID)

stop-all:
	-docker stop $(CONTAINER_HR) $(CONTAINER_EMP)-* 2>/dev/null

clean-db:
	rm -f $(DB_DIR)/database.db