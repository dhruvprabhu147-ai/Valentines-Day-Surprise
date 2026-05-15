Running the Valentine App

Recommended (uses project venv):

```bash
./run_streamlit.sh
```

Alternative (explicit venv python):

```bash
.venv/bin/python -m streamlit run MainApp.py
```

Or activate the venv and run normally:

```bash
source .venv/bin/activate
streamlit run MainApp.py
```

Notes:
- Streamlit is installed in the project's virtualenv (.venv). The `streamlit` CLI may not be on your shell PATH until you activate the venv.
- Config file: .streamlit/config.toml
