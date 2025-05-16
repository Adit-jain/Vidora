import sys
from pathlib import Path
base_dir = Path(__file__).parent.parent
sys.path.append(str(base_dir))
from backend.definitions import VideoMetadata
from backend.database import add_metadata_to_db
from backend.config import VIDEO_DIR
import uuid
import pandas as pd
from tqdm import tqdm

# Global Constants
MSRVTT_DIR = Path("D:\Datasets\MSRVTT_Video")
MSRVTT_METADATA_CSV = MSRVTT_DIR / "msrvtt_metadata.csv"
MSRVTT_VIDEO_DIR = MSRVTT_DIR / "Data"

# Read the metadata CSV file
metadata_df = pd.read_csv(MSRVTT_METADATA_CSV)

# Injest All videos from dir into the database
for vid_path in tqdm(MSRVTT_VIDEO_DIR.glob("*.mp4")):
    # Generate a unique video ID
    video_id = str(uuid.uuid4())

    # Get title and Description from the metadata CSV
    stem = vid_path.stem
    title = f'msrvtt_{stem}'
    description = metadata_df.loc[metadata_df['video_id'] == stem, 'caption'].values[0]
    if not description:
        description = title

    # Create a VideoMetadata object
    metadata = VideoMetadata(
        video_id=video_id,
        title=title,
        description=description,
        filename=vid_path.name,
        filepath=str(vid_path)
    )

    # Add metadata to the database
    add_metadata_to_db(video_id, metadata)




