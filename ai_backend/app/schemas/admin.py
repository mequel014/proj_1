# app/schemas/admin.py
from pydantic import BaseModel

class Stats(BaseModel):
    users: int
    characters: int
    dialogs: int
    messages: int