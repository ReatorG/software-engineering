import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
from uuid import UUID

class TranscripcionService:
    
    def __init__(self, base_path: str = "transcripciones"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        print(f"Directorio de transcripciones: {self.base_path.absolute()}")
    
    def guardar_transcripcion(
        self, 
        llamada_id: str, 
        transcripcion: str,
        customer_name: str = None,
        operator_name: str = None,
        start_at: datetime = None,
        end_at: datetime = None,
        palabras_clave: List[str] = None,
    ) -> str:
        filename = f"llamada_{llamada_id}.json"
        filepath = self.base_path / filename
        duracion_segundos = None
        duracion_minutos = None
        if start_at and end_at:
            delta = end_at - start_at
            duracion_segundos = delta.total_seconds()
            duracion_minutos = round(duracion_segundos / 60, 2)
        data = {
            "metadata": {
                "llamada_id": llamada_id,
                "customer_name": customer_name,
                "operator_name": operator_name,
                "start_at": start_at.isoformat() if start_at else None,
                "end_at": end_at.isoformat() if end_at else None,
                "duracion_segundos": duracion_segundos,
                "duracion_minutos": duracion_minutos,
                "palabras_clave": palabras_clave or [],
                "fecha_guardado": datetime.now().isoformat(),
                "version": "1.0"
            },
            "transcripcion": {
                "texto": transcripcion,
                "longitud_caracteres": len(transcripcion) if transcripcion else 0,
                "longitud_palabras": len(transcripcion.split()) if transcripcion else 0,
                "tiene_contenido": bool(transcripcion and transcripcion.strip())
            },
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"Transcripción guardada: {filename}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error guardando transcripción {llamada_id}: {e}")
            raise
    
    def leer_transcripcion_json(self, llamada_id: str) -> Optional[Dict[str, Any]]:
        filename = f"llamada_{llamada_id}.json"
        filepath = self.base_path / filename
        
        if not filepath.exists():
            print(f"No se encontró transcripción para llamada: {llamada_id}")
            return None
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Transcripción cargada: {llamada_id}")
            return data
            
        except json.JSONDecodeError as e:
            print(f"Error al leer JSON para {llamada_id}: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al leer {llamada_id}: {e}")
            return None
    
    def listar_transcripciones(self) -> list:
        archivos = []
        for archivo in self.base_path.iterdir():
            if archivo.is_file() and archivo.name.startswith('llamada_'):
                # Extrae el ID del nombre del archivo
                nombre = archivo.stem  # Sin extensión
                llamada_id = nombre.replace('llamada_', '')
                archivos.append({
                    'llamada_id': llamada_id,
                    'archivo': archivo.name,
                    'fecha_modificacion': datetime.fromtimestamp(archivo.stat().st_mtime)
                })
        
        return sorted(archivos, key=lambda x: x['fecha_modificacion'], reverse=True)
    
    def eliminar_transcripcion(self, llamada_id: str) -> bool:
        eliminados = 0

        for extension in ['.txt', '.json']:
            filename = f"llamada_{llamada_id}{extension}"
            filepath = self.base_path / filename
            
            if filepath.exists():
                filepath.unlink()
                eliminados += 1
        
        return eliminados > 0
