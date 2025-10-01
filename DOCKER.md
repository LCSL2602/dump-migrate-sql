# 🐳 Docker Setup - PostgreSQL Dump & Migrate Tool

Esta guía te permite ejecutar el script de dump-migrate-sql usando Docker, conectándote a tu servidor PostgreSQL externo.

## 📋 Requisitos

- Docker
- Docker Compose
- Acceso a un servidor PostgreSQL externo

## 🚀 Inicio Rápido

### 1. Configurar el entorno

```bash
# Copiar archivo de configuración
cp env.example .env

# Editar configuración con tus credenciales
nano .env
```

### 2. Configurar credenciales en `.env`

```env
# Configuración de conexión a PostgreSQL EXTERNO
DB_HOST=tu_servidor_postgresql.com
DB_PORT=5432
DB_NAME=tu_base_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña

# Configuración del dump (opcional)
DUMP_OUTPUT_DIR=./dumps
COMPRESS_DUMP=true
```

### 3. Construir y probar

```bash
# Construir la imagen
docker-compose build

# Probar conexión a tu servidor PostgreSQL
docker-compose run dump-script python main.py info
```

## 🛠️ Comandos Disponibles

### Comandos Básicos

```bash
# Ver ayuda
docker-compose run dump-script python main.py --help

# Ver información de la base de datos
docker-compose run dump-script python main.py info

# Crear dump completo
docker-compose run dump-script python main.py dump

# Crear dump solo esquema
docker-compose run dump-script python main.py dump --schema-only

# Crear dump solo datos
docker-compose run dump-script python main.py dump --data-only

# Crear dump formato personalizado
docker-compose run dump-script python main.py dump --custom-format
```

### Restaurar Dumps

```bash
# Restaurar un dump específico
docker-compose run dump-script python main.py restore dumps/dump_tu_bd_20241201_143022.sql

# Restaurar a una base de datos diferente
docker-compose run dump-script python main.py restore dumps/dump_tu_bd_20241201_143022.sql --target-db nueva_bd
```

### Ejecutar Ejemplos

```bash
# Ejecutar ejemplos de uso
docker-compose run dump-script python example_usage.py
```

## 🔧 Configuración Avanzada

### Usar Parámetros en Línea de Comandos

```bash
# Especificar servidor diferente en el comando
docker-compose run dump-script python main.py dump \
  --host otro_servidor.com \
  --port 5432 \
  --database otra_bd \
  --username otro_usuario \
  --password otra_contraseña
```

### Variables de Entorno Personalizadas

```bash
# Usar variables de entorno específicas
DB_HOST=mi_servidor.com DB_USER=mi_usuario docker-compose run dump-script python main.py info
```

## 📁 Estructura de Archivos

```
dump-migrate-sql/
├── Dockerfile              # Imagen del script
├── docker-compose.yml      # Configuración del servicio
├── env.example            # Ejemplo de configuración
├── dumps/                 # Directorio de dumps (montado como volumen)
└── .env                   # Tu configuración (crear desde env.example)
```

## 🧹 Limpieza

```bash
# Detener el servicio
docker-compose down

# Eliminar imagen construida
docker-compose down --rmi all
```

## 🐛 Solución de Problemas

### Error de Conexión

```bash
# Verificar conectividad desde el contenedor
docker-compose run dump-script ping tu_servidor_postgresql.com

# Probar conexión directa con psql
docker-compose run dump-script psql -h tu_servidor_postgresql.com -p 5432 -U tu_usuario -d tu_base_datos
```

### Error: "pg_dump: command not found"

```bash
# Reconstruir la imagen
docker-compose build --no-cache dump-script
```

### Problemas de Permisos

```bash
# Verificar permisos del directorio dumps
ls -la dumps/

# Si es necesario, cambiar permisos
chmod 755 dumps/
```

## 🔄 Flujo de Trabajo Típico

1. **Backup Regular**:
   ```bash
   docker-compose run dump-script python main.py dump
   ```

2. **Backup Programado**:
   ```bash
   # Agregar a crontab
   0 2 * * * cd /ruta/al/proyecto && docker-compose run dump-script python main.py dump
   ```

3. **Migración**:
   ```bash
   # Crear dump en servidor origen
   docker-compose run dump-script python main.py dump
   
   # Restaurar en servidor destino
   docker-compose run dump-script python main.py restore dumps/dump_*.sql
   ```

## 🎯 Casos de Uso

- **Backup Automatizado**: Scripts programados sin dependencias locales
- **Migración de Datos**: Entre diferentes servidores PostgreSQL
- **CI/CD**: Integración en pipelines de despliegue
- **Desarrollo**: Respaldo antes de cambios importantes
- **Producción**: Backups regulares de bases de datos críticas

## 📊 Monitoreo

```bash
# Ver logs del contenedor
docker-compose logs dump-script

# Ejecutar en modo interactivo para debugging
docker-compose run --rm dump-script bash
```
