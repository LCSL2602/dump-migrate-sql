# PostgreSQL Dump & Migrate Tool

Una herramienta completa en Python para hacer dump y restaurar bases de datos PostgreSQL de manera fácil y eficiente.

## 🚀 Características

- ✅ **Dump completo**: Respaldo completo de la base de datos
- ✅ **Múltiples formatos**: SQL comprimido, SQL plano, formato personalizado
- ✅ **Opciones flexibles**: Solo esquema, solo datos, o completo
- ✅ **Restauración**: Restaurar dumps fácilmente
- ✅ **Información de BD**: Ver detalles de la base de datos
- ✅ **Configuración simple**: Archivo .env para credenciales
- ✅ **CLI amigable**: Interfaz de línea de comandos intuitiva
- ✅ **Manejo de errores**: Logging detallado y manejo robusto de errores

## 📋 Requisitos

- Python 3.13+
- PostgreSQL 9.6+
- Herramientas de PostgreSQL instaladas (`pg_dump`, `pg_restore`, `psql`)

## 🔧 Instalación

1. **Clona o descarga el proyecto**:
   ```bash
   cd dump-migrate-sql
   ```

2. **Instala las dependencias**:
   ```bash
   pip install -e .
   ```

3. **Configura el entorno**:
   ```bash
   python main.py setup
   ```

4. **Edita el archivo `.env`** con tus credenciales:
   ```bash
   nano .env
   ```

## ⚙️ Configuración

El archivo `.env` debe contener:

```env
# Servidor de base de datos
DB_HOST=localhost
DB_PORT=5432

# Credenciales de la base de datos
DB_NAME=mi_base_datos
DB_USER=mi_usuario
DB_PASSWORD=mi_contraseña

# Configuración del dump (opcional)
DUMP_OUTPUT_DIR=./dumps
COMPRESS_DUMP=true
```

## 📖 Uso

### Comandos disponibles

```bash
# Ver ayuda general
python main.py --help

# Configurar el entorno (primera vez)
python main.py setup

# Ver información de la base de datos
python main.py info

# Crear un dump
python main.py dump

# Restaurar un dump
python main.py restore archivo_dump.sql
```

### Crear Dumps

**Dump completo (recomendado)**:
```bash
python main.py dump
```

**Solo esquema (estructura)**:
```bash
python main.py dump --schema-only
```

**Solo datos**:
```bash
python main.py dump --data-only
```

**Formato personalizado (binario, más eficiente)**:
```bash
python main.py dump --custom-format
```

**Especificar archivo de salida**:
```bash
python main.py dump --output mi_respaldo.sql
```

**Con parámetros personalizados**:
```bash
python main.py dump --host mi-servidor.com --port 5432 --database mi_bd --username mi_usuario --password mi_password
```

### Restaurar Dumps

**Restaurar a la misma base de datos**:
```bash
python main.py restore dump_mi_bd_20241201_143022.sql
```

**Restaurar a una base de datos diferente**:
```bash
python main.py restore dump_mi_bd_20241201_143022.sql --target-db nueva_base_datos
```

**Sobrescribir completamente una base de datos destino (con backup automático de seguridad y confirmación)**:
```bash
python main.py restore dump_mi_bd_20241201_143022.sql --target-db nueva_base_datos --overwrite-full
```

**Restaurar dump en formato personalizado**:
```bash
python main.py restore dump_mi_bd_20241201_143022.dump
```

### Ver información de la base de datos

```bash
python main.py info
```

## 📁 Estructura de archivos

```
dump-migrate-sql/
├── main.py                 # Interfaz de línea de comandos
├── postgresql_dumper.py    # Clase principal para dump/restore
├── config.py              # Configuración y manejo de variables de entorno
├── pyproject.toml         # Dependencias del proyecto
├── env_example.txt        # Ejemplo de archivo de configuración
├── README.md              # Este archivo
└── dumps/                 # Directorio donde se guardan los dumps
    └── dump_*_*.sql       # Archivos de dump generados
```

## 🔍 Tipos de dump disponibles

1. **SQL Comprimido** (`.sql.gz`): Formato estándar comprimido con gzip
2. **SQL Plano** (`.sql`): Formato SQL estándar sin comprimir
3. **Formato Personalizado** (`.dump`): Formato binario de PostgreSQL (más eficiente)

## 🛠️ Funcionalidades técnicas

### PostgreSQLDumper Class

La clase principal incluye:

- **Conexión automática**: Manejo robusto de conexiones
- **Context manager**: Uso seguro con `with`
- **Información de BD**: Obtener detalles de la base de datos
- **Múltiples formatos**: SQL, comprimido, y formato personalizado
- **Restauración**: Soporte para todos los formatos
- **Logging**: Registro detallado de operaciones
- **Manejo de errores**: Gestión completa de excepciones

### Métodos principales

```python
# Conexión
dumper = PostgreSQLDumper(host, port, database, username, password)
dumper.connect()

# Información
info = dumper.get_database_info()

# Dumps
dumper.create_dump(output_file, schema_only, data_only, compress)
dumper.create_custom_dump(output_file)

# Restauración
dumper.restore_dump(dump_file, target_database)

# Uso como context manager
with PostgreSQLDumper(...) as dumper:
    dumper.create_dump()
```

## 🚨 Solución de problemas

### Error: "pg_dump: command not found"
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# CentOS/RHEL
sudo yum install postgresql

# macOS
brew install postgresql
```

### Error de conexión
- Verifica que PostgreSQL esté ejecutándose
- Confirma las credenciales en el archivo `.env`
- Verifica que el usuario tenga permisos de acceso

### Error de permisos
```sql
-- Conectar como superusuario y otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE mi_base_datos TO mi_usuario;
```

## 📝 Ejemplos de uso

### Script automatizado de backup

```python
from postgresql_dumper import PostgreSQLDumper
from config import DEFAULT_CONFIG

# Configuración
config = DEFAULT_CONFIG

# Crear dump programáticamente
with PostgreSQLDumper(
    host=config.host,
    port=config.port,
    database=config.database,
    username=config.username,
    password=config.password
) as dumper:
    
    # Obtener información
    info = dumper.get_database_info()
    print(f"Dumping {info['database']} ({info['size']})")
    
    # Crear dump
    success = dumper.create_dump(compress=True)
    if success:
        print("Backup completado exitosamente")
    else:
        print("Error en el backup")
```

### Backup programado con cron

```bash
# Agregar al crontab para backup diario a las 2 AM
0 2 * * * cd /ruta/al/proyecto && python main.py dump
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- PostgreSQL por la excelente herramienta `pg_dump`
- La comunidad de Python por las librerías utilizadas
- Todos los contribuidores que han mejorado este proyecto
