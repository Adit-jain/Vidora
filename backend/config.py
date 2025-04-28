from pathlib import Path

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_DIR = BASE_DIR / "storage"
METADATA_DIR = BASE_DIR / "metadata"
CHUNK_SIZE = 1024 * 1024  # 1MB chunk size for streaming