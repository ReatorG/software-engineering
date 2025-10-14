from fastapi import FastAPI, HTTPException
from datetime import datetime
from uuid import uuid4
from typing import List
from pydantic import BaseModel
from APP.Infrastructure.database import db_manager
from APP.Infrastructure.TranscripcionService import TranscripcionService
from APP.Application.Analisis import analizar_llamada

app = FastAPI(title="API de Gestión de Llamadas", version="1.0.0")

# Servicios
transcripcion_service = TranscripcionService()

# Modelos Pydantic
class LlamadaCreate(BaseModel):
    customer_name: str
    operator_name: str = None
    start_at: datetime
    end_at: datetime = None
    palabras_clave: List[str] = []
    transcripcion: str = None

class LlamadaResponse(BaseModel):
    id: str
    customer_name: str
    operator_name: str = None
    start_at: datetime
    end_at: datetime = None
    duration_seconds: float = None
    palabras_clave: List[str] = []
    transcripcion_archivo: str = None
    created_at: datetime = None

# ENDPOINTS
@app.post("/llamadas/", response_model=LlamadaResponse)
def crear_llamada(llamada: LlamadaCreate):
    """
    Crea una nueva llamada y opcionalmente guarda su transcripción.
    """
    try:
        llamada_id = str(uuid4())
        
        # Preparar datos para la base de datos
        llamada_data = {
            'id': llamada_id,
            'customer_name': llamada.customer_name,
            'operator_name': llamada.operator_name,
            'start_at': llamada.start_at.isoformat(),
            'end_at': llamada.end_at.isoformat() if llamada.end_at else None,
            'palabras_clave': llamada.palabras_clave
        }
        
        # Guardar transcripción si existe
        transcripcion_archivo = None
        if llamada.transcripcion:
            transcripcion_archivo = transcripcion_service.guardar_transcripcion(
                llamada_id=llamada_id,
                transcripcion=llamada.transcripcion,
                customer_name=llamada.customer_name,
                operator_name=llamada.operator_name,
                start_at=llamada.start_at,
                end_at=llamada.end_at,
                palabras_clave=llamada.palabras_clave
            )
            llamada_data['transcripcion_archivo'] = transcripcion_archivo
        
        # Guardar en base de datos
        db_manager.guardar_llamada(llamada_data)
        
        # Devolver respuesta
        return LlamadaResponse(
            id=llamada_id,
            **llamada.dict(),
            transcripcion_archivo=transcripcion_archivo
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando llamada: {str(e)}")

@app.get("/llamadas/{llamada_id}", response_model=LlamadaResponse)
def obtener_llamada(llamada_id: str):
    """
    Obtiene una llamada específica por su ID.
    """
    llamada = db_manager.obtener_llamada(llamada_id)
    if not llamada:
        raise HTTPException(status_code=404, detail="Llamada no encontrada")
    
    return LlamadaResponse(**llamada)

@app.get("/llamadas/", response_model=List[LlamadaResponse])
def listar_llamadas(limit: int = 50):
    """
    Lista las llamadas más recientes.
    """
    llamadas = db_manager.listar_llamadas(limit=limit)
    return [LlamadaResponse(**llamada) for llamada in llamadas]

@app.post("/llamadas/{llamada_id}/analizar")
def analizar_llamada_endpoint(llamada_id: str):
    """
    Analiza la transcripción de una llamada usando ML.
    """
    try:
        # Obtener la llamada
        llamada = db_manager.obtener_llamada(llamada_id)
        if not llamada:
            raise HTTPException(status_code=404, detail="Llamada no encontrada")
        
        # Obtener la transcripción
        if not llamada.get('transcripcion_archivo'):
            raise HTTPException(status_code=400, detail="La llamada no tiene transcripción")
        
        transcripcion_data = transcripcion_service.leer_transcripcion_json(llamada_id)
        if not transcripcion_data:
            raise HTTPException(status_code=404, detail="Transcripción no encontrada")
        
        # Analizar con ML
        transcripcion_texto = transcripcion_data['transcripcion']['texto']
        resultado_analisis = analizar_llamada(transcripcion_texto)
        
        # Guardar resultado en base de datos
        analisis_id = db_manager.guardar_analisis(llamada_id, resultado_analisis)
        
        return {
            "mensaje": "Análisis completado",
            "analisis_id": analisis_id,
            "llamada_id": llamada_id,
            "resultado": resultado_analisis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")

@app.get("/llamadas/{llamada_id}/analisis")
def obtener_analisis(llamada_id: str):
    """
    Obtiene el análisis más reciente de una llamada.
    """
    analisis = db_manager.obtener_analisis(llamada_id)
    if not analisis:
        raise HTTPException(status_code=404, detail="No se encontró análisis para esta llamada")
    
    return analisis

@app.get("/operadores/{operator_name}/estadisticas")
def obtener_estadisticas_operador(operator_name: str):
    """
    Obtiene estadísticas de un operador específico.
    """
    estadisticas = db_manager.obtener_estadisticas_operador(operator_name)
    if not estadisticas.get('total_llamadas'):
        raise HTTPException(status_code=404, detail="No se encontraron datos para este operador")
    
    return estadisticas

# Health check
@app.get("/health")
def health_check():
    """Endpoint de salud de la API."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}