import psycopg2
import psycopg2.extras
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from config import settings

class DatabaseManager:
    
    def __init__(self):
        self.connection_params = {
            'host': settings.database_host,
            'port': settings.database_port,
            'database': settings.database_name,
            'user': settings.database_user,
            'password': settings.database_password
        }
        
        self._test_connection()
        self._create_tables()
        logging.info(f"PostgreSQL conectado: {settings.database_host}:{settings.database_port}")
    
    def _get_connection(self):
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except psycopg2.Error as e:
            logging.error(f"Error conectando a PostgreSQL: {e}")
            raise
    
    def _test_connection(self):
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    logging.info(f"Conexión PostgreSQL exitosa: {version}")
        except Exception as e:
            logging.error(f"Error conectando a PostgreSQL: {e}")
            raise
    
    def _create_tables(self):
        """Crea las tablas necesarias en PostgreSQL."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS llamadas (
                        id VARCHAR(255) PRIMARY KEY,
                        customer_name VARCHAR(255) NOT NULL,
                        operator_name VARCHAR(255),
                        start_at TIMESTAMP NOT NULL,
                        end_at TIMESTAMP,
                        duration_seconds REAL,
                        palabras_clave JSONB,  -- JSON nativo de PostgreSQL
                        transcripcion_archivo TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analisis_llamadas (
                        id SERIAL PRIMARY KEY,
                        llamada_id VARCHAR(255) NOT NULL,
                        regulacion_cumplimiento INTEGER,
                        regulacion_comentario TEXT,
                        habilidad_comercial INTEGER,
                        habilidad_comentario TEXT,
                        conocimiento_producto INTEGER,
                        conocimiento_comentario TEXT,
                        cierre_venta INTEGER,
                        cierre_comentario TEXT,
                        puntuacion_general INTEGER,
                        aspectos_positivos JSONB,
                        areas_mejora JSONB,
                        recomendacion TEXT,
                        modelo_usado VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (llamada_id) REFERENCES llamadas (id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS operadores (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL UNIQUE,
                        email VARCHAR(255),
                        departamento VARCHAR(255),
                        activo BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_llamadas_operator 
                    ON llamadas (operator_name)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_llamadas_created_at 
                    ON llamadas (created_at DESC)
                """)
                
                conn.commit()
                logging.info("Tablas PostgreSQL creadas/verificadas")


    def guardar_llamada(self, llamada_data: Dict[str, Any]) -> str:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                duration = None
                if llamada_data.get('start_at') and llamada_data.get('end_at'):
                    start = datetime.fromisoformat(llamada_data['start_at'].replace('Z', '+00:00'))
                    end = datetime.fromisoformat(llamada_data['end_at'].replace('Z', '+00:00'))
                    duration = (end - start).total_seconds()
                
                cursor.execute("""
                    INSERT INTO llamadas 
                    (id, customer_name, operator_name, start_at, end_at, 
                     duration_seconds, palabras_clave, transcripcion_archivo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    llamada_data['id'],
                    llamada_data['customer_name'],
                    llamada_data.get('operator_name'),
                    llamada_data['start_at'],
                    llamada_data.get('end_at'),
                    duration,
                    json.dumps(llamada_data.get('palabras_clave', [])),
                    llamada_data.get('transcripcion_archivo')
                ))
                
                conn.commit()
                logging.info(f"Llamada guardada: {llamada_data['id']}")
                return llamada_data['id']
    
    def obtener_llamada(self, llamada_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM llamadas WHERE id = %s
                """, (llamada_id,))
                
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    return data
                return None
    
    def listar_llamadas(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM llamadas 
                    ORDER BY created_at DESC 
                    LIMIT %s
                """, (limit,))
                
                llamadas = []
                for row in cursor.fetchall():
                    data = dict(row)
                    llamadas.append(data)
                
                return llamadas
    
    def guardar_analisis(self, llamada_id: str, analisis_data: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO analisis_llamadas 
                    (llamada_id, regulacion_cumplimiento, regulacion_comentario,
                     habilidad_comercial, habilidad_comentario, conocimiento_producto,
                     conocimiento_comentario, cierre_venta, cierre_comentario,
                     puntuacion_general, aspectos_positivos, areas_mejora,
                     recomendacion, modelo_usado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    llamada_id,
                    analisis_data.get('regulacion', {}).get('cumplimiento'),
                    analisis_data.get('regulacion', {}).get('comentario'),
                    analisis_data.get('habilidad_comercial', {}).get('puntuacion'),
                    analisis_data.get('habilidad_comercial', {}).get('comentario'),
                    analisis_data.get('conocimiento_producto', {}).get('puntuacion'),
                    analisis_data.get('conocimiento_producto', {}).get('comentario'),
                    analisis_data.get('cierre_venta', {}).get('puntuacion'),
                    analisis_data.get('cierre_venta', {}).get('comentario'),
                    analisis_data.get('puntuacion_general'),
                    json.dumps(analisis_data.get('aspectos_positivos', [])),
                    json.dumps(analisis_data.get('areas_mejora', [])),
                    analisis_data.get('recomendacion'),
                    settings.ml_model_name
                ))
                
                analisis_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Análisis guardado: {analisis_id} para llamada {llamada_id}")
                return analisis_id
    
    def obtener_analisis(self, llamada_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM analisis_llamadas 
                    WHERE llamada_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (llamada_id,))
                
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    if data.get('aspectos_positivos') and isinstance(data['aspectos_positivos'], str):
                        data['aspectos_positivos'] = json.loads(data['aspectos_positivos'])
                    if data.get('areas_mejora') and isinstance(data['areas_mejora'], str):
                        data['areas_mejora'] = json.loads(data['areas_mejora'])
                    return data
                return None

    def obtener_estadisticas_operador(self, operator_name: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(l.id) as total_llamadas,
                        ROUND(AVG(a.puntuacion_general), 2) as promedio_puntuacion,
                        ROUND(AVG(l.duration_seconds), 2) as duracion_promedio,
                        ROUND(AVG(a.regulacion_cumplimiento), 2) as promedio_regulacion,
                        ROUND(AVG(a.habilidad_comercial), 2) as promedio_habilidad,
                        ROUND(AVG(a.conocimiento_producto), 2) as promedio_conocimiento,
                        ROUND(AVG(a.cierre_venta), 2) as promedio_cierre
                    FROM llamadas l
                    LEFT JOIN analisis_llamadas a ON l.id = a.llamada_id
                    WHERE l.operator_name = %s
                """, (operator_name,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return {}

db_manager = DatabaseManager()
