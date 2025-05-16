from backend.definitions import VideoMetadata
from pathlib import Path
import pandas as pd
from backend.config import METADATA_DIR
METADATA_CSV = METADATA_DIR / "metadata.csv"

# ------------ Metadata CSV Management ------------- #
def create_METADATA_CSV():
    """
    Creates a CSV file for storing video metadata.
    """
    df = pd.DataFrame(columns=["video_id", "title", "description", "filename", "filepath"])
    df.to_csv(METADATA_CSV, index=False)
    print(f"Metadata CSV file created at {METADATA_CSV}")
    return df

def read_metadata_from_csv():
    """
    Reads metadata from a CSV file and returns it as a list of VideoMetadata objects.
    """
    if not METADATA_CSV.exists():
        print(f"Metadata CSV file not found: {METADATA_CSV}")
        df = create_METADATA_CSV()
    else:
        df = pd.read_csv(METADATA_CSV)
    return df

def write_metadata_to_csv(df: pd.DataFrame):
    """
    Writes the DataFrame to a CSV file.
    """
    if not METADATA_DIR.exists():
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(METADATA_CSV, index=False)


# ------------ Metadata Operations ------------- #
def list_videos_from_db():
    """
    Returns a list of all video metadata from the in-memory database.
    """
    df = read_metadata_from_csv()
    return df['video_id'].tolist()

def add_metadata_to_db(video_id, metadata: VideoMetadata):
    """
    Adds metadata to the in-memory database.
    """
    df = read_metadata_from_csv()

    # Video ID already exists, delete the old entry
    if len(df[df['video_id'] == video_id]) > 0:
        df = df[df['video_id'] != video_id]
        print(f"Video ID {video_id} already exists in CSV. Deleting old entry.")

    # Append new metadata
    data = metadata.model_dump()
    df.loc[len(df)] = data
    write_metadata_to_csv(df)

def get_metadata_from_db(video_id):
    """
    Retrieves metadata for a specific video ID from the in-memory database.
    """
    df = read_metadata_from_csv()
    video_metadata = df[df['video_id'] == video_id]
    if video_metadata.empty:
        return None
    video_metadata = video_metadata.iloc[0].to_dict()
    return video_metadata