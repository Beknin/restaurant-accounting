VENV_DIR = .venv
SETUP_CMD ?= ./scripts/setup.sh
CLEAN_CMD ?= ./scripts/clean.sh
BUILD_LIB_CMD ?= ./scripts/build-lib.sh
RUN_CMD ?= ./scripts/run.sh
FORMAT_CMD ?= ./scripts/format.sh
TESTS_CMD ?= ./scripts/tests.sh

.PHONY: setup clean run build-lib format run-tests

help:
	@printf '%s\n' \
		'setup              Prepare local environment' \
		'run                Run the application' \
		'test               Run tests' \
		'coverage           Generate test coverage report' \
		'build-lib          Build reusable component' \
		'publish-lib        Publish reusable component' \
		'install-lib-local  Install locally built component into consumer' \
		'docs               Build documentation and diagrams' \
		'compose-up         Build and start container stack' \
		'compose-down       Stop and clean container stack' \
		'check              Full local verification' \
		'clean              Remove generated artifacts'

setup:
	$(SETUP_CMD)

clean: $(VENV_DIR)
	$(CLEAN_CMD)

run: $(VENV_DIR)
	$(RUN_CMD)

build-lib: $(VENV_DIR)
	$(BUILD_LIB_CMD)

format: $(VENV_DIR)
	$(FORMAT_CMD)

run-tests: $(VENV_DIR)
	$(TESTS_CMD)