from backend.definitions import VideoMetadata

# --- In-memory storage for video metadata (Replace with a database in production) ---
# Structure: { "video_id": {"id": "...", "title": "...", "description": "...", "filename": "..."} }
videos_db = {}

def list_videos_from_db():
    """
    Returns a list of all video metadata from the in-memory database.
    """
    return list(videos_db.values())

def add_metadata_to_db(video_id, metadata: VideoMetadata):
    """
    Adds metadata to the in-memory database.
    """
    videos_db[video_id] = metadata.model_dump()
    print(f"Added metadata for video ID {video_id}: {metadata}")

def get_metadata_from_db(video_id):
    """
    Retrieves metadata for a specific video ID from the in-memory database.
    """
    return videos_db.get(video_id, None)