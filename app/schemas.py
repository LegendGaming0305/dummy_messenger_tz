from pydantic import BaseModel
from datetime import datetime

class MessageBase(BaseModel):
    sender: str
    text: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    created_at: datetime
    sequence_number: int
    user_counter: int