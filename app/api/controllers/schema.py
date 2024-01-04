"""
schema
"""
from typing import Optional
from pydantic import BaseModel

class Metadata(BaseModel):
    job_id: Optional[str] = "1"
    chatbot_type: Optional[str] = "1"
    job_location: Optional[str] = None
    ip_address: str = None
    client_id: str = None
    # channel : str

class RasaWebhook(BaseModel):
    sender: str
    message: str
    metadata : Optional[Metadata] = Metadata()