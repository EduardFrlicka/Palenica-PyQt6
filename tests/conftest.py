"""The application is a script tree, not a package: src/ is what ends up on
sys.path when app.py runs, and the modules import each other flatly."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
