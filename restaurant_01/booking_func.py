from llama_index.core.bridge.pydantic import BaseModel
from typing import Optional

class Booking(BaseModel):
    name: Optional[str] = None
    phone: Optional[int] = None

    
    