# Usar Python 3.13 slim como base
FROM python:3.13-slim

# Instalar dependencias del sistema necesarias para PostgreSQL
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY pyproject.toml ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir -e .

# Copiar código fuente
COPY . .

# Crear directorio para dumps
RUN mkdir -p /app/dumps

# Hacer el script ejecutable
RUN chmod +x main.py

# Comando por defecto
CMD ["python", "main.py", "--help"]
