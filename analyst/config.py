import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

RAW_DIR = ROOT / "data" / "raw"
CHROMA_DIR = ROOT / "data" / "chroma"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
COLLECTION = "reports_bge_small_v1"

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to your .env file.")
    return value



