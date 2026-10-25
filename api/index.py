import sys
from pathlib import Path

# vercel runs this file from the repo root, so point python at the backend package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.main import create_app  # noqa: E402

app = create_app()
