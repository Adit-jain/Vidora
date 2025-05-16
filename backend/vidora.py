import sys
from pathlib import Path
BASE_DIR = str(Path(__file__).resolve().parent.parent)
sys.path.append(BASE_DIR)

import uuid
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Header, status, Form
from fastapi.middleware.cors import CORSMiddleware # If you need frontend interaction
from backend.config import VIDEO_DIR
from backend.utils import save_file, file_exists, get_file_size, stream_video_range
from backend.definitions import VideoMetadata, VideoUploadResponse
from backend.database import add_metadata_to_db, list_videos_from_db, get_metadata_from_db

# --- FastAPI App --- #
app = FastAPI(title="Simple Video Streaming API")

# --- CORS Middleware --- #
origins = [
    "http://localhost",
    "http://localhost:8080", # Example frontend origin
    "http://127.0.0.1:5500", # Example for VS Code Live Server
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints --- #
@app.post("/upload/", response_model=VideoUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    """
    Uploads a video file along with its title and description.
    Stores the video locally and saves metadata in memory.
    """
    if not file.content_type.startswith("video/"):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only video files are allowed.")

    video_id = str(uuid.uuid4())
    original_filename = file.filename or "untitled" # Secure filename handling could be improved (e.g., removing special chars)
    filename = f"{video_id}_{original_filename}" # Add unique ID to filename to prevent collisions
    file_path = VIDEO_DIR / filename

    # Save file to local storage
    await save_file(file, file_path)

    # Store metadata in our "DB"
    metadata = VideoMetadata(
        video_id=video_id,
        title=title,
        description=description,
        filename=filename,
        filepath = str(file_path)
    )
    add_metadata_to_db(video_id, metadata)

    # Response
    print(f"Uploaded video: {metadata.title} (ID: {video_id}, Filename: {filename})")
    return VideoUploadResponse(video_id=video_id, title=title, description=description)

@app.get("/videos/", response_model=List[str])
async def list_videos():
    """
    Returns a list of metadata for all available videos.
    """
    vid_list = list_videos_from_db()
    print(vid_list)
    return vid_list

@app.get("/videos/{video_id}", response_model=VideoMetadata)
async def get_video_metadata(video_id: str) -> VideoMetadata:
    """
    Returns metadata for a specific video by ID.
    """
    metadata = get_metadata_from_db(video_id)
    if metadata is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")
    return metadata

@app.get("/stream/{video_id}")
async def stream_video(video_id: str, request: Request, range: Optional[str] = Header(None)):
    """
    Streams the video content. Handles HTTP Range requests for seeking.
    """
    video_metadata = await get_video_metadata(video_id)
    file_name = video_metadata['filename']
    file_path = Path(video_metadata['filepath'])
    file_exists(file_path, throw_exception=True) # Ensure metadata exists before streaming
    file_size = get_file_size(file_path)

    return stream_video_range(file_path, file_name, file_size, range)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Vidora"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)