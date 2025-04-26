from typing import List, Optional
from pydantic import BaseModel

# --- Pydantic Models --- #
class VideoMetadata(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    filename: str
    filepath: str

class VideoUploadResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None