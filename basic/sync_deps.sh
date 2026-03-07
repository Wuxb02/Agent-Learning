#!/bin/bash

cd "$(dirname "$0")"

echo "==> Freezing dependencies..."
uv pip freeze > requirements.txt

echo "==> Adding dependencies to pyproject.toml..."
uv add -r requirements.txt

echo "==> Done!"
