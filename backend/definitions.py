from typing import List, Optional
from pydantic import BaseModel

# --- Pydantic Models --- #
class VideoMetadata(BaseModel):
    video_id: str
    title: str
    description: Optional[str] = None
    filename: str
    filepath: str

class VideoUploadResponse(BaseModel):
    video_id: str
    title: str
    description: Optional[str] = None