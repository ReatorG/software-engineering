# src/app/call/dto/create_call_request_dto.py
from pydantic import BaseModel
from enum import Enum

class CallDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"

class CreateCallRequestDto(BaseModel):
    agent_id: int
    client_phone: str
    direction: CallDirection
