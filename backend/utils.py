from backend.config import CHUNK_SIZE
import aiofiles # For async file operations
from pathlib import Path
from fastapi import HTTPException, status, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse

# --- Helper Function for Streaming ---
async def send_bytes_range_requests(
    file_path: Path, start: int, end: int, chunk_size: int = CHUNK_SIZE
):
    """
    Sends chunks of bytes based on start/end. Used for Range requests.
    """
    async with aiofiles.open(file_path, mode="rb") as file:
        await file.seek(start)
        while (pos := await file.tell()) <= end:
            read_size = min(chunk_size, end - pos + 1)
            # Check if bytes needs to be read or not
            if read_size <= 0:
                break
            yield await file.read(read_size)

def stream_video_range(file_path: Path, file_name: str, file_size: int = None, range: str = None):
    """
    Streams the video content. Handles HTTP Range requests for seeking.
    """
    headers = {
        'Content-Type': 'video/mp4', # Assume mp4, adjust if needed or detect dynamically
        'Accept-Ranges': 'bytes',
        'Content-Length': str(file_size),
        'Connection': 'keep-alive',
    }

    # Handle Range requests
    start, end = 0, file_size - 1
    status_code = status.HTTP_200_OK

    if range:
        range_header = range.replace("bytes=", "")
        start_str, end_str = range_header.split("-")[:2]
        start = int(start_str) if start_str else 0
        end = int(end_str) if end_str else file_size - 1

        # Check validity of range
        if start >= file_size or end >= file_size or start > end:
             raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                                 detail=f"Invalid range requested: {range}")

        # Adjust headers for partial content
        headers['Content-Length'] = str(end - start + 1)
        headers['Content-Range'] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT
        print(f"Streaming range: {start}-{end} for {file_name}")

    else:
        print(f"Streaming entire file: {file_name}")

    # Streaming Resoponse
    return StreamingResponse(
        send_bytes_range_requests(file_path, start, end),
        status_code=status_code,
        headers=headers,
        media_type="video/mp4" # Important for browser player
    )


# --- Helper Function for File Handling --- #
async def save_file(file: UploadFile, file_path: Path):
    try:
        # Save the file asynchronously
        async with aiofiles.open(file_path, "wb") as buffer:
            while content := await file.read(CHUNK_SIZE):
                await buffer.write(content)
    except Exception as e:
        # Clean up if saving fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not save file: {e}")
    finally:
        await file.close() # Ensure file descriptor is closed

def file_exists(file_path: Path, throw_exception = True) -> bool:
    """
    Check if a file exists at the given path.
    """
    if not file_path.is_file():
        if throw_exception:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video file not found on server")
        else:
            return False
    return True

def get_file_size(file_path: Path) -> int:
    """
    Get the size of the file in bytes.
    """
    # Get file size
    try:
        file_size = file_path.stat().st_size
    except Exception as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error accessing file stats: {e}")
    
    return file_size