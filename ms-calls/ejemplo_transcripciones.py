"""
Ejemplo de uso del TranscripcionService
"""
from APP.Domain.Llamda import Llamda
from APP.Infrastructure.TranscripcionService import TranscripcionService
from datetime import datetime

def ejemplo_uso_basico():
    """Ejemplo básico de guardado y lectura"""
    print("=== Ejemplo 1: Uso básico ===")
    
    # Crear el servicio
    servicio = TranscripcionService()
    
    # Simular una llamada
    llamada_id = "123e4567-e89b-12d3-a456-426614174000"
    transcripcion = """
    Operador: Buenos días, ¿en qué le puedo ayudar?
    Cliente: Hola, tengo un problema con mi factura.
    Operador: Por supuesto, ¿me puede dar su número de cuenta?
    Cliente: Sí, es el 123456789.
    Operador: Perfecto, veo que tiene un cargo pendiente...
    """
    
    # Guardar transcripción simple
    archivo_txt = servicio.guardar_transcripcion_simple(llamada_id, transcripcion)
    print(f"Guardado en: {archivo_txt}")
    
    # Leer transcripción
    contenido = servicio.leer_transcripcion_simple(llamada_id)
    print(f"Contenido leído: {contenido[:100]}...")

def ejemplo_uso_avanzado():
    """Ejemplo con JSON y metadata"""
    print("\n=== Ejemplo 2: Con metadata ===")
    
    servicio = TranscripcionService()
    llamada_id = "456g7890-h12i-34j5-k678-901234567890"
    
    transcripcion = "Cliente muy satisfecho con el servicio..."
    metadata = {
        "cliente": "María García",
        "operador": "Juan Pérez",
        "duracion_minutos": 15,
        "categoria": "Soporte técnico"
    }
    
    # Guardar con metadata
    archivo_json = servicio.guardar_transcripcion_json(llamada_id, transcripcion, metadata)
    print(f"Guardado JSON en: {archivo_json}")
    
    # Leer con metadata
    data = servicio.leer_transcripcion_json(llamada_id)
    print(f"Metadata: {data['metadata']}")

def ejemplo_con_modelo_llamada():
    """Ejemplo usando el modelo Llamada directamente"""
    print("\n=== Ejemplo 3: Con modelo Llamada ===")
    
    # Crear una llamada
    llamada = Llamda(
        customer_name="Ana López",
        operator_name="Carlos Ruiz",
        start_at=datetime.now(),
        transcripcion="Esta es una transcripción de ejemplo muy larga..."
    )
    
    # Guardar automáticamente
    archivo = llamada.guardar_transcripcion()
    print(f"Llamada guardada automáticamente en: {archivo}")
    
    # Crear otra llamada sin transcripción
    llamada2 = Llamda(
        customer_name="Pedro Martín", 
        start_at=datetime.now()
    )
    
    # Intentar cargar transcripción existente
    if llamada2.cargar_transcripcion():
        print("Transcripción cargada exitosamente")
    else:
        print("No se encontró transcripción para esta llamada")

def ejemplo_listado():
    """Ejemplo de listado de transcripciones"""
    print("\n=== Ejemplo 4: Listado ===")
    
    servicio = TranscripcionService()
    transcripciones = servicio.listar_transcripciones()
    
    print(f"Se encontraron {len(transcripciones)} transcripciones:")
    for trans in transcripciones:
        print(f"- {trans['llamada_id']} ({trans['archivo']}) - {trans['fecha_modificacion']}")

if __name__ == "__main__":
    # Ejecutar ejemplos
    ejemplo_uso_basico()
    ejemplo_uso_avanzado() 
    ejemplo_con_modelo_llamada()
    ejemplo_listado()
