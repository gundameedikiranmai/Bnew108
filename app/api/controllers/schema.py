"""
schema
"""
from typing import Optional
from pydantic import BaseModel

class Metadata(BaseModel):
    job_id: str
    chatbot_type: "str"
    job_location: Optional["str"]
    # email: str
    # channel : str

class RasaWebhook(BaseModel):
    sender: str
    message: str
    metadata : Optional[Metadata] = Metadata(job_id="1", chatbot_type="1", job_location=None)