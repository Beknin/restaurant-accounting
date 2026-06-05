IMAGE_NAME = restaurant-app
IMAGE_TAG = latest
CONTAINER_NAME_HR = restaurant-hr
CONTAINER_NAME_EMP_PREFIX = restaurant-emp
DB_DIR = ./infra/db
DB_FILE = $(DB_DIR)/database.db
PYTHON = python3
MAIN_SCRIPT = app/ui/main.py

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make build              - Build Docker image"
	@echo "  make rebuild            - Rebuild Docker image without cache"
	@echo "  make run-hr             - Run HR panel (Docker)"
	@echo "  make run-employee ID=5  - Run employee panel (Docker)"
	@echo "  make run-local-hr       - Run HR panel (local)"
	@echo "  make run-local-employee ID=5 - Run employee panel (local)"
	@echo "  make run-local-login    - Run with login screen (local)"
	@echo "  make compose-hr         - Run HR via docker-compose"
	@echo "  make compose-employee ID=5 - Run employee via docker-compose"
	@echo "  make test               - Run all tests"
	@echo "  make test-unit          - Run unit tests"
	@echo "  make test-smoke         - Run smoke tests"
	@echo "  make install            - Install dependencies via poetry"
	@echo "  make stop-hr            - Stop HR container"
	@echo "  make stop-employee ID=5 - Stop employee container"
	@echo "  make stop-all           - Stop all containers"
	@echo "  make logs-hr            - Show HR container logs"
	@echo "  make logs-employee ID=5 - Show employee container logs"
	@echo "  make clean              - Remove containers and image"
	@echo "  make clean-db           - Remove database"
	@echo "  make setup              - Full environment setup"

.PHONY: build
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: rebuild
rebuild:
	docker build --no-cache -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: run-hr
run-hr:
	xhost +local:docker > /dev/null 2>&1 || true
	docker run --rm -it \
		--name $(CONTAINER_NAME_HR) \
		-e DISPLAY=$(DISPLAY) \
		-e ROLE=hr \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v $(PWD)/$(DB_DIR):/app/infra/db \
		--network host \
		$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: run-employee
run-employee:
	@if [ -z "$(ID)" ]; then \
		echo "Error: Specify employee ID: make run-employee ID=5"; \
		exit 1; \
	fi
	xhost +local:docker > /dev/null 2>&1 || true
	docker run --rm -it \
		--name $(CONTAINER_NAME_EMP_PREFIX)-$(ID) \
		-e DISPLAY=$(DISPLAY) \
		-e ROLE=employee \
		-e EMPLOYEE_ID=$(ID) \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v $(PWD)/$(DB_DIR):/app/infra/db \
		--network host \
		$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: compose-hr
compose-hr:
	docker-compose up hr-panel

.PHONY: compose-employee
compose-employee:
	@if [ -z "$(ID)" ]; then \
		echo "Error: Specify employee ID: make compose-employee ID=5"; \
		exit 1; \
	fi
	EMPLOYEE_ID=$(ID) docker-compose --profile employee up employee-panel

.PHONY: install
install:
	poetry install --only main

.PHONY: install-dev
install-dev:
	poetry install

.PHONY: run-local-hr
run-local-hr: install
	ROLE=hr $(PYTHON) $(MAIN_SCRIPT)

.PHONY: run-local-employee
run-local-employee: install
	@if [ -z "$(ID)" ]; then \
		echo "Error: Specify employee ID: make run-local-employee ID=5"; \
		exit 1; \
	fi
	ROLE=employee EMPLOYEE_ID=$(ID) $(PYTHON) $(MAIN_SCRIPT)

.PHONY: run-local-login
run-local-login: install
	$(PYTHON) $(MAIN_SCRIPT)

.PHONY: test
test: install-dev
	poetry run pytest tests/ -v

.PHONY: test-unit
test-unit: install-dev
	poetry run pytest tests/unit/ -v

.PHONY: test-smoke
test-smoke: install-dev
	poetry run pytest tests/smoke/ -v

.PHONY: stop-hr
stop-hr:
	-docker stop $(CONTAINER_NAME_HR)

.PHONY: stop-employee
stop-employee:
	@if [ -z "$(ID)" ]; then \
		echo "Error: Specify employee ID: make stop-employee ID=5"; \
		exit 1; \
	fi
	-docker stop $(CONTAINER_NAME_EMP_PREFIX)-$(ID)

.PHONY: stop-all
stop-all:
	-docker ps --filter "name=$(CONTAINER_NAME_HR)" --filter "name=$(CONTAINER_NAME_EMP_PREFIX)" -q | xargs -r docker stop
	-docker-compose down

.PHONY: logs-hr
logs-hr:
	docker logs -f $(CONTAINER_NAME_HR)

.PHONY: logs-employee
logs-employee:
	@if [ -z "$(ID)" ]; then \
		echo "Error: Specify employee ID: make logs-employee ID=5"; \
		exit 1; \
	fi
	docker logs -f $(CONTAINER_NAME_EMP_PREFIX)-$(ID)

.PHONY: clean
clean: stop-all
	-docker rmi $(IMAGE_NAME):$(IMAGE_TAG)
	-docker-compose down -v

.PHONY: clean-db
clean-db:
	rm -f $(DB_FILE)

.PHONY: clean-pycache
clean-pycache:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

.PHONY: setup
setup: build install
	@mkdir -p $(DB_DIR)
	xhost +local:docker > /dev/null 2>&1 || true

.PHONY: dev-setup
dev-setup: setup install-dev
	@echo "Development environment ready"