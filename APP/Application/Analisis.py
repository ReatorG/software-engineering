
import json
import logging
import torch
from APP.Domain.ModelManager import ModelManager
from config import settings

def analizar_llamada(transcripcion: str) -> dict:
    """
    Analiza una transcripción de llamada usando el modelo ML.
    
    Args:
        transcripcion: Texto de la conversación a analizar
        
    Returns:
        dict: Resultado del análisis con métricas y evaluaciones
    """
    try:
        # Usar ModelManager para reutilizar el modelo cargado
        manager = ModelManager()
        tokenizer, model = manager.get_model()
        
        # Prompt más conciso y enfocado en JSON
        prompt = f"""[INST] Analiza esta transcripción de llamada y devuelve SOLO un JSON válido con estas métricas:

{{
  "regulacion": {{
    "cumplimiento": 0-10,
    "comentario": "breve explicación"
  }},
  "habilidad_comercial": {{
    "puntuacion": 0-10,
    "comentario": "breve explicación"
  }},
  "conocimiento_producto": {{
    "puntuacion": 0-10,
    "comentario": "breve explicación"
  }},
  "cierre_venta": {{
    "puntuacion": 0-10,
    "comentario": "breve explicación"
  }},
  "puntuacion_general": 0-10,
  "aspectos_positivos": ["aspecto1", "aspecto2"],
  "areas_mejora": ["mejora1", "mejora2"],
  "recomendacion": "recomendación final"
}}

Transcripción: {transcripcion}
[/INST]"""

        # Tokenizar y generar
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():  # Ahorra memoria
            outputs = model.generate(
                **inputs,
                max_new_tokens=settings.max_new_tokens,
                do_sample=False,
                repetition_penalty=1.05,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decodificar respuesta
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extraer solo la parte JSON (después del prompt)
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_response = response[json_start:json_end]
            result = json.loads(json_response)
            logging.info(f"Análisis completado exitosamente")
            return result
        else:
            logging.warning("No se encontró JSON válido en la respuesta")
            return {
                "error": "No se pudo extraer JSON de la respuesta",
                "raw_response": response
            }
            
    except json.JSONDecodeError as e:
        logging.error(f"Error parseando JSON: {e}")
        return {
            "error": "Respuesta no es JSON válido",
            "parse_error": str(e),
            "raw_response": response if 'response' in locals() else "Sin respuesta"
        }
    except Exception as e:
        logging.error(f"Error en análisis de llamada: {e}")
        return {
            "error": "Error inesperado en el análisis",
            "exception": str(e)
        }


def analizar_llamada_simple(transcripcion: str) -> str:
    """
    Versión simple que devuelve texto plano (para debugging).
    
    Args:
        transcripcion: Texto de la conversación
        
    Returns:
        str: Análisis en texto plano
    """
    try:
        manager = ModelManager()
        tokenizer, model = manager.get_model()
        
        prompt = f"""[INST] Analiza brevemente esta transcripción de llamada del 1-10:

Transcripción: {transcripcion}
[/INST]"""

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extraer solo la respuesta (después del prompt)
        response_start = response.find("[/INST]") + 7
        return response[response_start:].strip() if response_start > 6 else response
        
    except Exception as e:
        return f"Error en análisis simple: {str(e)}"
