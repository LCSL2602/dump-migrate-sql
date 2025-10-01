"""
Configuración para el dumper de PostgreSQL
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()


class DatabaseConfig:
    """Configuración de la base de datos PostgreSQL"""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'postgres')
        self.username = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        
        # Configuración de dump
        self.dump_output_dir = os.getenv('DUMP_OUTPUT_DIR', './dumps')
        self.compress_dump = os.getenv('COMPRESS_DUMP', 'true').lower() == 'true'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'password': self.password
        }
    
    def validate(self) -> bool:
        """Valida que la configuración sea correcta"""
        if not self.password:
            print("Error: DB_PASSWORD no está configurada")
            return False
        
        if not self.database:
            print("Error: DB_NAME no está configurada")
            return False
        
        return True
    
    def create_dump_directory(self):
        """Crea el directorio de dumps si no existe"""
        if not os.path.exists(self.dump_output_dir):
            os.makedirs(self.dump_output_dir)
            print(f"Directorio de dumps creado: {self.dump_output_dir}")


# Configuración por defecto
DEFAULT_CONFIG = DatabaseConfig()
