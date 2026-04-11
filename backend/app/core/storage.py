from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
UPLOADS_ROOT = BACKEND_ROOT / "uploads"


def ensure_uploads_root() -> Path:
    """Ensure uploads root exists and return it."""
    UPLOADS_ROOT.mkdir(parents=True, exist_ok=True)
    return UPLOADS_ROOT


def ensure_uploads_subdir(*parts: str) -> Path:
    """Ensure uploads subdirectory exists and return it."""
    base = ensure_uploads_root()
    target = base.joinpath(*parts)
    target.mkdir(parents=True, exist_ok=True)
    return target