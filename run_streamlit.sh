#!/usr/bin/env bash
# Run the Streamlit app using the project's virtualenv Python
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$SCRIPT_DIR/.venv/bin/python"

if [ ! -x "$VENV_PY" ]; then
	echo "Error: virtualenv Python not found at $VENV_PY"
	echo "Create the virtualenv or install dependencies into .venv first."
	exit 1
fi

if [ "${1-}" = "--version" ] || [ "${1-}" = "-v" ]; then
	exec "$VENV_PY" -m streamlit --version
fi

if ! "$VENV_PY" -c "import streamlit" >/dev/null 2>&1; then
	echo "Streamlit not found in .venv — installing..."
	"$VENV_PY" -m pip install --upgrade pip
	"$VENV_PY" -m pip install streamlit
fi

exec "$VENV_PY" -m streamlit run "$SCRIPT_DIR/MainApp.py" "$@"
