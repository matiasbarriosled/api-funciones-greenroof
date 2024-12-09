from fastapi import FastAPI

from routers import download_mapics

app = FastAPI()
app.include_router(download_mapics)