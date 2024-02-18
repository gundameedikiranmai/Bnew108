from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from controllers.routers import router as api_router
from config.conf import settings


app = FastAPI()

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    # allow_origins=settings.origins.get('origins'),
    allow_origin_regex=r"/*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "Online"}


# ---------------------
# Health check endpoint
# ---------------------
@app.get("/health", include_in_schema=False)
def health_check():
    return {'status': 'ok'}