
import json
import logging
import torch
from APP.Domain.ModelManager import ModelManager
from config import settings

def analizar_llamada(transcripcion: str) -> dict:
    try:

        manager = ModelManager()
        tokenizer, model = manager.get_model()
        
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

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=settings.max_new_tokens,
                do_sample=False,
                repetition_penalty=1.05,
                pad_token_id=tokenizer.eos_token_id
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

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



