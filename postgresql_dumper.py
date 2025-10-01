import os
import subprocess
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class PostgreSQLDumper:
    """
    Clase para realizar dump completo de bases de datos PostgreSQL
    """
    
    def __init__(self, host: str, port: int, database: str, username: str, password: str):
        """
        Inicializa el dumper con los parámetros de conexión
        
        Args:
            host: Dirección del servidor PostgreSQL
            port: Puerto del servidor (por defecto 5432)
            database: Nombre de la base de datos
            username: Usuario para la conexión
            password: Contraseña del usuario
        """
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        Establece conexión con la base de datos PostgreSQL
        
        Returns:
            bool: True si la conexión es exitosa, False en caso contrario
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.logger.info(f"Conexión establecida con éxito a {self.host}:{self.port}/{self.database}")
            return True
        except psycopg2.Error as e:
            self.logger.error(f"Error al conectar a la base de datos: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self.connection:
            self.connection.close()
            self.logger.info("Conexión cerrada")
    
    def get_database_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información básica de la base de datos
        
        Returns:
            Dict con información de la base de datos o None si hay error
        """
        if not self.connection:
            self.logger.error("No hay conexión establecida")
            return None
        
        try:
            cursor = self.connection.cursor()
            
            # Obtener información de la base de datos
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
            db_info = cursor.fetchone()
            
            cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
            size = cursor.fetchone()[0]
            
            cursor.close()
            
            info = {
                'version': version,
                'database': db_info[0],
                'user': db_info[1],
                'server_host': db_info[2],
                'server_port': db_info[3],
                'size': size
            }
            
            self.logger.info(f"Información de la base de datos obtenida: {info['database']} ({info['size']})")
            return info
            
        except psycopg2.Error as e:
            self.logger.error(f"Error al obtener información de la base de datos: {e}")
            return None
    
    def create_dump(self, output_file: Optional[str] = None, 
                   schema_only: bool = False, data_only: bool = False,
                   compress: bool = True) -> bool:
        """
        Crea un dump completo de la base de datos usando pg_dump
        
        Args:
            output_file: Archivo de salida (opcional, se genera automáticamente si no se especifica)
            schema_only: Si True, solo incluye el esquema (sin datos)
            data_only: Si True, solo incluye los datos (sin esquema)
            compress: Si True, comprime el archivo de salida
            
        Returns:
            bool: True si el dump se creó exitosamente, False en caso contrario
        """
        if not self.connection:
            self.logger.error("No hay conexión establecida")
            return False
        
        # Generar nombre de archivo si no se especifica
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"dump_{self.database}_{timestamp}.sql"
            if compress:
                output_file += ".gz"
        
        # Construir comando pg_dump
        cmd = [
            'pg_dump',
            '-h', self.host,
            '-p', str(self.port),
            '-U', self.username,
            '-d', self.database
        ]
        
        # Agregar opciones según los parámetros
        if schema_only:
            cmd.append('-s')
        elif data_only:
            cmd.append('-a')
        
        # Opciones adicionales para un dump completo
        if not schema_only and not data_only:
            cmd.extend(['--clean', '--if-exists', '--create'])
        
        cmd.extend(['--verbose', '--no-password'])
        
        # Configurar variables de entorno
        env = os.environ.copy()
        env['PGPASSWORD'] = self.password
        
        try:
            self.logger.info(f"Iniciando dump de la base de datos {self.database}...")
            self.logger.info(f"Comando: {' '.join(cmd[:-2])} [password hidden]")
            
            if compress and output_file.endswith('.gz'):
                # Usar compresión con gzip
                import gzip
                with gzip.open(output_file, 'wt', encoding='utf-8') as f:
                    process = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        env=env,
                        check=True
                    )
            else:
                # Sin compresión
                with open(output_file, 'w', encoding='utf-8') as f:
                    process = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        env=env,
                        check=True
                    )
            
            # Obtener el tamaño del archivo creado
            file_size = os.path.getsize(output_file)
            size_mb = file_size / (1024 * 1024)
            
            self.logger.info(f"Dump completado exitosamente: {output_file}")
            self.logger.info(f"Tamaño del archivo: {size_mb:.2f} MB")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error al ejecutar pg_dump: {e}")
            self.logger.error(f"Stderr: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado durante el dump: {e}")
            return False
    
    def create_custom_dump(self, output_file: Optional[str] = None) -> bool:
        """
        Crea un dump en formato personalizado (binario) usando pg_dump -Fc
        
        Args:
            output_file: Archivo de salida (opcional, se genera automáticamente si no se especifica)
            
        Returns:
            bool: True si el dump se creó exitosamente, False en caso contrario
        """
        if not self.connection:
            self.logger.error("No hay conexión establecida")
            return False
        
        # Generar nombre de archivo si no se especifica
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"dump_{self.database}_{timestamp}.dump"
        
        # Construir comando pg_dump con formato personalizado
        cmd = [
            'pg_dump',
            '-h', self.host,
            '-p', str(self.port),
            '-U', self.username,
            '-d', self.database,
            '-Fc',  # Formato personalizado
            '--verbose',
            '--no-password'
        ]
        
        # Configurar variables de entorno
        env = os.environ.copy()
        env['PGPASSWORD'] = self.password
        
        try:
            self.logger.info(f"Iniciando dump personalizado de la base de datos {self.database}...")
            
            with open(output_file, 'wb') as f:
                process = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    check=True
                )
            
            # Obtener el tamaño del archivo creado
            file_size = os.path.getsize(output_file)
            size_mb = file_size / (1024 * 1024)
            
            self.logger.info(f"Dump personalizado completado exitosamente: {output_file}")
            self.logger.info(f"Tamaño del archivo: {size_mb:.2f} MB")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error al ejecutar pg_dump: {e}")
            self.logger.error(f"Stderr: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado durante el dump personalizado: {e}")
            return False
    
    def restore_dump(self, dump_file: str, target_database: Optional[str] = None) -> bool:
        """
        Restaura un dump de la base de datos
        
        Args:
            dump_file: Archivo de dump a restaurar
            target_database: Base de datos de destino (opcional, usa la misma si no se especifica)
            
        Returns:
            bool: True si la restauración fue exitosa, False en caso contrario
        """
        if not target_database:
            target_database = self.database
        
        # Determinar si es un archivo comprimido o formato personalizado
        if dump_file.endswith('.gz'):
            # Archivo SQL comprimido
            import gzip
            cmd = ['psql']
            input_file = gzip.open(dump_file, 'rt', encoding='utf-8')
        elif dump_file.endswith('.dump'):
            # Formato personalizado
            cmd = ['pg_restore']
            input_file = None
        else:
            # Archivo SQL normal
            cmd = ['psql']
            input_file = open(dump_file, 'r', encoding='utf-8')
        
        # Construir comando de restauración
        cmd.extend([
            '-h', self.host,
            '-p', str(self.port),
            '-U', self.username,
            '-d', target_database,
            '--verbose',
            '--no-password'
        ])
        
        # Configurar variables de entorno
        env = os.environ.copy()
        env['PGPASSWORD'] = self.password
        
        try:
            self.logger.info(f"Iniciando restauración desde {dump_file} a {target_database}...")
            
            if input_file:
                process = subprocess.run(
                    cmd,
                    stdin=input_file,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    check=True
                )
                input_file.close()
            else:
                process = subprocess.run(
                    cmd + [dump_file],
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    check=True
                )
            
            self.logger.info("Restauración completada exitosamente")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error al restaurar el dump: {e}")
            self.logger.error(f"Stderr: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado durante la restauración: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
