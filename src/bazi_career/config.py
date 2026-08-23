import os
from pathlib import Path

def get_data_dir() -> Path:
    """Return the local data directory for the application."""
    # Use standard user data directory, fallback to ~/.bazi-career
    if os.name == "nt":
        appdata = os.environ.get("LOCALAPPDATA")
        if appdata:
            return Path(appdata) / "bazi-career"
    elif os.name == "posix":
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            return Path(xdg_data) / "bazi-career"
        
    return Path.home() / ".bazi-career"

DATA_DIR = get_data_dir()
DB_PATH = DATA_DIR / "bazi_career.db"
