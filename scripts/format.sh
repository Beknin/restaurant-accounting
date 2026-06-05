#!/bin/bash
.venv/bin/pip install black
.venv/bin/black --check app/
.venv/bin/black --check packages/