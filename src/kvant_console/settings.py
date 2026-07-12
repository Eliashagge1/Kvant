from pathlib import Path
import os
HOME=Path(os.environ.get("KVANT_HOME", Path.home()/".kvant"))
DB=Path(os.environ.get("KVANT_DB", HOME/"kvant.duckdb"))
CONFIG=Path(os.environ.get("KVANT_CONFIG", HOME/"universe.json"))
RESEARCH=Path(os.environ.get("KVANT_RESEARCH", HOME/"research"))
ARTIFACTS=Path(os.environ.get("KVANT_ARTIFACTS", HOME/"artifacts"))
SERVICE="KvantConsole"; KEY_USER="alpha_vantage_api_key"
def ensure_dirs():
    for p in (HOME,RESEARCH,ARTIFACTS): p.mkdir(parents=True,exist_ok=True)
