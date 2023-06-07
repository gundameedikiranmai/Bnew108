"""
schema
"""
from typing import Optional
from pydantic import BaseModel

# class Metadata(BaseModel):
#     email: str
#     channel : str

class RasaWebhook(BaseModel):
    sender: str
    message: str
    # metadata : Metadata