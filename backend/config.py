from pathlib import Path

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent
VIDEO_DIR = BASE_DIR / "videos"
CHUNK_SIZE = 1024 * 1024  # 1MB chunk size for streaming