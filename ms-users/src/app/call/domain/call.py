# src/app/call/domain/call.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class CallDirection(Enum):
    INBOUND = "INBOUND"    # Cliente llama al call center
    OUTBOUND = "OUTBOUND"  # Agente llama al cliente

class CallStatus(Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    ERROR = "ERROR"

@dataclass
class Call:
    id: Optional[int]
    agent_id: int
    client_phone: str
    direction: CallDirection
    status: CallStatus = CallStatus.QUEUED
    is_sale: bool = False
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    audio_file_url: Optional[str] = None
    resumen_ai: Optional[str] = None
    created_at: datetime = datetime.utcnow()
