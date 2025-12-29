from pathlib import Path

from fastapi import HTTPException
from starlette.responses import FileResponse

from app.webserver.main import app


@app.get("/", response_class=FileResponse)
async def get_root():
    """Return the resources HTML page."""
    html_path = Path(__file__).parent.parent / "electron" / "index.html"
    return FileResponse(html_path)


@app.get("/download", response_class=FileResponse)
async def download_input_overlay():
    """Return the Electron installer as a downloadable file."""
    file_path = Path(__file__).parent.parent / "electron" / "dist" / "InputOverlay Setup 1.0.0.exe"
    return FileResponse(
        path=file_path,
        filename="InputOverlay.exe",  # Name shown to the user
        media_type="application/octet-stream"
    )


@app.get("/js/{file_path:path}", response_class=FileResponse)
async def get_js(file_path: str):
    """
    Return a JavaScript file from the ``resources/js`` directory.

    Example: ``GET /js/app.js`` → ``resources/js/app.js``.
    """
    js_path = Path(__file__).parent.parent / "electron" / "js" / file_path
    if not js_path.is_file():
        raise HTTPException(status_code=404, detail="JavaScript file not found")
    return FileResponse(js_path, media_type="application/javascript")
