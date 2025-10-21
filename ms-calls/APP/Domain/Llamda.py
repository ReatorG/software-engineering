from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class Llamda(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the Llamda")
    customer_name: str = Field(..., description="Name of the customer")
    operator_name: Optional[str] = Field(None, description="Name of the operator")
    start_at: datetime = Field(..., description="Start time of the Llamda")
    end_at: Optional[datetime] = Field(None, description="End time of the Llamda")
    palabras_clave: Optional[list[str]] = Field(None, description="Keywords associated with the Llamda")
    transcripcion: Optional[str] = Field(None, description="Transcription of the Llamda")

    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "customer_name": "John Doe",
                "operator_name": "Jane Smith",
                "start_at": "2023-01-01T00:00:00Z",
                "end_at": "2023-01-02T00:00:00Z",
                "palabras_clave": ["keyword1", "keyword2"]
            }
        }
    def duration(self) -> Optional[float]:
        """Calculate the duration of the Llamda in hours."""
        if self.end_at and self.start_at:
            delta = self.end_at - self.start_at
            return delta.total_seconds() / 3600
        return None
    
    def guardar_transcripcion(self, servicio_transcripcion=None) -> Optional[str]:
        """
        Guarda la transcripción en un archivo si existe.
        
        Args:
            servicio_transcripcion: Instancia del TranscripcionService
            
        Returns:
            str: Ruta del archivo guardado o None si no hay transcripción
        """
        if not self.transcripcion:
            return None
        
        if not servicio_transcripcion:
            from APP.Infrastructure.TranscripcionService import TranscripcionService
            servicio_transcripcion = TranscripcionService()
        
        metadata = {
            "customer_name": self.customer_name,
            "operator_name": self.operator_name,
            "start_at": self.start_at.isoformat(),
            "end_at": self.end_at.isoformat() if self.end_at else None,
            "duration_hours": self.duration(),
            "palabras_clave": self.palabras_clave
        }
        
        return servicio_transcripcion.guardar_transcripcion_json(
            str(self.id), 
            self.transcripcion, 
            metadata
        )
    
    def cargar_transcripcion(self, servicio_transcripcion=None) -> bool:
        """
        Carga la transcripción desde archivo si existe.
        
        Args:
            servicio_transcripcion: Instancia del TranscripcionService
            
        Returns:
            bool: True si se cargó la transcripción, False si no existía
        """
        if not servicio_transcripcion:
            from APP.Infrastructure.TranscripcionService import TranscripcionService
            servicio_transcripcion = TranscripcionService()
        
        data = servicio_transcripcion.leer_transcripcion_json(str(self.id))
        
        if data:
            self.transcripcion = data["transcripcion"]
            return True
        
        return False
