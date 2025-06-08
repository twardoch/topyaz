#!/usr/bin/env bash

python -m uzpy run -e src
fd -e py -x autoflake {}
fd -e py -x pyupgrade --py311-plus {}
fd -e py -x ruff check --output-format=github --fix --unsafe-fixes {}
fd -e py -x ruff format --respect-gitignore --target-version py311 {}
repomix -i varia,.specstory,AGENT.md,CLAUDE.md,PLAN.md,llms.txt,.cursorrules -o llms.txt .
python -m pytest
