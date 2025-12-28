from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.webserver.managers import listener_manager

app = FastAPI()
def init_app():
    listener_manager.init_app()
    import routes  # noqa
    import websocket  # noqa

    return app



if __name__ == "__main__":
    uvicorn.run("app.webserver.main:init_app", host="0.0.0.0", port=7790, reload=True)
