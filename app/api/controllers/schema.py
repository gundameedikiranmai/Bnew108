"""
schema
"""
from typing import Optional
from pydantic import BaseModel

class Metadata(BaseModel):
    job_id: str
    # email: str
    # channel : str

class RasaWebhook(BaseModel):
    sender: str
    message: str
    metadata : Optional[Metadata] = {"job_id": "1"}