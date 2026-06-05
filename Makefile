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
		-v $(PWD)/infra/db:/app/infra/db \
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
		-v $(PWD)/infra/db:/app/infra/db \
		--network host \
		$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: run-local-hr
run-local-hr:
	ROLE=hr $(PYTHON) $(MAIN_SCRIPT)

.PHONY: run-local-employee
run-local-employee:
	@if [ -z "$(ID)" ]; then \
		echo "Error: Specify employee ID: make run-local-employee ID=5"; \
		exit 1; \
	fi
	ROLE=employee EMPLOYEE_ID=$(ID) $(PYTHON) $(MAIN_SCRIPT)

.PHONY: run-local-login
run-local-login:
	$(PYTHON) $(MAIN_SCRIPT)

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

.PHONY: clean-db
clean-db:
	rm -f $(DB_FILE)

.PHONY: setup
setup: build
	@mkdir -p $(DB_DIR)
	xhost +local:docker > /dev/null 2>&1 || true