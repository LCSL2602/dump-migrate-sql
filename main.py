#!/usr/bin/env python3
"""
Herramienta para hacer dump y restauración de bases de datos PostgreSQL
"""

import click
import os
from datetime import datetime
from postgresql_dumper import PostgreSQLDumper
from config import DEFAULT_CONFIG


@click.group()
def cli():
    """Herramienta para dump y migración de PostgreSQL"""
    pass


@cli.command()
@click.option('--host', default=None, help='Host del servidor PostgreSQL')
@click.option('--port', default=None, type=int, help='Puerto del servidor PostgreSQL')
@click.option('--database', default=None, help='Nombre de la base de datos')
@click.option('--username', default=None, help='Usuario de la base de datos')
@click.option('--password', default=None, help='Contraseña de la base de datos')
@click.option('--output', '-o', default=None, help='Archivo de salida para el dump')
@click.option('--schema-only', is_flag=True, help='Solo incluir esquema (sin datos)')
@click.option('--data-only', is_flag=True, help='Solo incluir datos (sin esquema)')
@click.option('--compress', is_flag=True, default=True, help='Comprimir el archivo de dump')
@click.option('--custom-format', is_flag=True, help='Usar formato personalizado (binario)')
def dump(host, port, database, username, password, output, schema_only, data_only, compress, custom_format):
    """Crear un dump de la base de datos PostgreSQL"""
    
    # Usar configuración por defecto si no se especifican parámetros
    config = DEFAULT_CONFIG
    if host:
        config.host = host
    if port:
        config.port = port
    if database:
        config.database = database
    if username:
        config.username = username
    if password:
        config.password = password
    
    # Validar configuración
    if not config.validate():
        click.echo("Error: Configuración de base de datos incompleta", err=True)
        return
    
    # Crear directorio de dumps si no existe
    config.create_dump_directory()
    
    # Generar nombre de archivo si no se especifica
    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_format:
            output = os.path.join(config.dump_output_dir, f"dump_{config.database}_{timestamp}.dump")
        else:
            extension = ".sql.gz" if compress else ".sql"
            output = os.path.join(config.dump_output_dir, f"dump_{config.database}_{timestamp}{extension}")
    
    try:
        with PostgreSQLDumper(
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=config.password
        ) as dumper:
            
            # Mostrar información de la base de datos
            info = dumper.get_database_info()
            if info:
                click.echo(f"Conectado a: {info['database']} en {info['server_host']}:{info['server_port']}")
                click.echo(f"Tamaño: {info['size']}")
            
            # Crear dump según el formato especificado
            if custom_format:
                success = dumper.create_custom_dump(output)
            else:
                success = dumper.create_dump(
                    output_file=output,
                    schema_only=schema_only,
                    data_only=data_only,
                    compress=compress
                )
            
            if success:
                click.echo(f"✅ Dump completado exitosamente: {output}")
            else:
                click.echo("❌ Error al crear el dump", err=True)
                return
                
    except Exception as e:
        click.echo(f"❌ Error inesperado: {e}", err=True)


@cli.command()
@click.option('--host', default=None, help='Host del servidor PostgreSQL')
@click.option('--port', default=None, type=int, help='Puerto del servidor PostgreSQL')
@click.option('--database', default=None, help='Nombre de la base de datos')
@click.option('--username', default=None, help='Usuario de la base de datos')
@click.option('--password', default=None, help='Contraseña de la base de datos')
@click.argument('dump_file', type=click.Path(exists=True))
@click.option('--target-db', help='Base de datos de destino (por defecto usa la misma)')
@click.option('--overwrite-full', is_flag=True, help='Sobrescribe completamente la DB destino (con backup de seguridad previo)')
def restore(host, port, database, username, password, dump_file, target_db, overwrite_full):
    """Restaurar un dump de la base de datos PostgreSQL"""
    
    # Usar configuración por defecto si no se especifican parámetros
    config = DEFAULT_CONFIG
    if host:
        config.host = host
    if port:
        config.port = port
    if database:
        config.database = database
    if username:
        config.username = username
    if password:
        config.password = password
    
    # Validar configuración
    if not config.validate():
        click.echo("Error: Configuración de base de datos incompleta", err=True)
        return
    
    try:
        with PostgreSQLDumper(
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=config.password
        ) as dumper:
            
            target_database = target_db or config.database
            click.echo(f"Restaurando {dump_file} en {target_database}...")

            if overwrite_full:
                config.create_dump_directory()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(
                    config.dump_output_dir,
                    f"backup_before_overwrite_{target_database}_{timestamp}.sql.gz"
                )

                click.echo("\n⚠️  MODO SOBRESCRITURA TOTAL ACTIVADO")
                click.echo(f"Se creará backup de seguridad en: {backup_file}")
                click.echo(f"Luego se eliminará y recreará la base de datos destino: {target_database}")
                click.confirm("¿Estás seguro que quieres continuar?", default=False, abort=True)

                click.echo("\n🔒 Creando backup de seguridad antes de sobrescribir...")
                backup_success = dumper.backup_database(
                    database_name=target_database,
                    output_file=backup_file,
                    compress=True
                )

                if not backup_success:
                    click.echo("❌ No se pudo crear el backup de seguridad. Operación cancelada.", err=True)
                    return

                click.echo("🧹 Eliminando y recreando base de datos destino...")
                recreate_success = dumper.recreate_database(target_database)
                if not recreate_success:
                    click.echo("❌ No se pudo recrear la base de datos destino. Operación cancelada.", err=True)
                    return
            
            success = dumper.restore_dump(dump_file, target_database)
            
            if success:
                click.echo("✅ Restauración completada exitosamente")
            else:
                click.echo("❌ Error al restaurar el dump", err=True)
                
    except Exception as e:
        click.echo(f"❌ Error inesperado: {e}", err=True)


@cli.command()
@click.option('--host', default=None, help='Host del servidor PostgreSQL')
@click.option('--port', default=None, type=int, help='Puerto del servidor PostgreSQL')
@click.option('--database', default=None, help='Nombre de la base de datos')
@click.option('--username', default=None, help='Usuario de la base de datos')
@click.option('--password', default=None, help='Contraseña de la base de datos')
def info(host, port, database, username, password):
    """Mostrar información de la base de datos PostgreSQL"""
    
    # Usar configuración por defecto si no se especifican parámetros
    config = DEFAULT_CONFIG
    if host:
        config.host = host
    if port:
        config.port = port
    if database:
        config.database = database
    if username:
        config.username = username
    if password:
        config.password = password
    
    # Validar configuración
    if not config.validate():
        click.echo("Error: Configuración de base de datos incompleta", err=True)
        return
    
    try:
        with PostgreSQLDumper(
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=config.password
        ) as dumper:
            
            info = dumper.get_database_info()
            if info:
                click.echo("📊 Información de la Base de Datos:")
                click.echo(f"  Base de datos: {info['database']}")
                click.echo(f"  Usuario: {info['user']}")
                click.echo(f"  Servidor: {info['server_host']}:{info['server_port']}")
                click.echo(f"  Tamaño: {info['size']}")
                click.echo(f"  Versión: {info['version']}")
            else:
                click.echo("❌ No se pudo obtener información de la base de datos", err=True)
                
    except Exception as e:
        click.echo(f"❌ Error inesperado: {e}", err=True)


@cli.command()
def setup():
    """Configurar el entorno para el dumper"""
    click.echo("🔧 Configurando el entorno...")
    
    # Crear archivo .env si no existe
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""# Configuración de conexión a PostgreSQL
# Configura estos valores según tu entorno

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
""")
        click.echo("✅ Archivo .env creado. Por favor, configura tus valores de conexión.")
    else:
        click.echo("ℹ️  El archivo .env ya existe.")
    
    # Crear directorio de dumps
    config = DEFAULT_CONFIG
    config.create_dump_directory()
    
    click.echo("✅ Configuración completada.")
    click.echo("\n📝 Próximos pasos:")
    click.echo("1. Edita el archivo .env con tus credenciales de PostgreSQL")
    click.echo("2. Ejecuta: python main.py info (para probar la conexión)")
    click.echo("3. Ejecuta: python main.py dump (para crear un dump)")


def main():
    """Función principal"""
    cli()


if __name__ == "__main__":
    main()
