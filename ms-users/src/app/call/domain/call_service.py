from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.call.infrastructure.call_repository import CallRepository

class CallService:
    def __init__(self, repository: CallRepository):
        self.repository = repository

    # =============================
    # CREATE
    # =============================
    def create_call(self, agent_id: int, client_phone: str, direction: str) -> Dict[str, Any]:
        """
        Crea una llamada iniciada por un agente o cliente.
        """
        # Validar datos básicos
        if not client_phone or len(client_phone) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client phone number"
            )

        if direction not in ("INBOUND", "OUTBOUND"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid direction. Must be 'INBOUND' or 'OUTBOUND'."
            )

        # Crear la llamada
        call = self.repository.create_call(
            agent_id=agent_id,
            client_phone=client_phone,
            direction=direction,
            status="QUEUED",
            start_time=datetime.now(timezone.utc).isoformat()
        )

        return call

    # =============================
    # READ
    # =============================
    def get_call_by_id(self, call_id: int) -> Dict[str, Any]:
        call = self.repository.get_call_by_id(call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Call with ID {call_id} not found"
            )
        return call

    def list_calls(self, page: int = 1, page_size: int = 10,
                   direction: Optional[str] = None,
                   status: Optional[str] = None,
                   agent_id: Optional[int] = None) -> tuple[List[Dict[str, Any]], int]:
        """
        Listar llamadas con filtros y paginación.
        """
        skip = (page - 1) * page_size
        calls = self.repository.get_all_calls(
            skip=skip,
            limit=page_size,
            direction=direction,
            status=status,
            agent_id=agent_id
        )
        total = self.repository.count_calls(
            direction=direction,
            status=status,
            agent_id=agent_id
        )
        return calls, total

    # =============================
    # UPDATE
    # =============================
    def update_call(self, call_id: int, **kwargs) -> Dict[str, Any]:
        """
        Actualizar información de la llamada:
        - cambiar estado
        - marcar venta
        - agregar resumen o audio
        """
        call = self.repository.get_call_by_id(call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )

        updated_call = self.repository.update_call(call, **kwargs)
        return updated_call

    # =============================
    # DELETE
    # =============================
    def delete_call(self, call_id: int) -> None:
        """
        Eliminar una llamada (solo pruebas o limpieza).
        """
        call = self.repository.get_call_by_id(call_id)
        if not call:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Call not found"
            )

        self.repository.delete_call(call_id)
