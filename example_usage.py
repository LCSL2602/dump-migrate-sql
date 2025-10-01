#!/usr/bin/env python3
"""
Ejemplo de uso del PostgreSQL Dumper
"""

from postgresql_dumper import PostgreSQLDumper
from config import DEFAULT_CONFIG
import os


def example_basic_usage():
    """Ejemplo básico de uso del dumper"""
    print("=== Ejemplo Básico de Uso ===")
    
    # Configuración (usa variables de entorno o valores por defecto)
    config = DEFAULT_CONFIG
    
    # Verificar configuración
    if not config.validate():
        print("❌ Configuración incompleta. Ejecuta 'python main.py setup' primero.")
        return
    
    try:
        # Usar el dumper como context manager (recomendado)
        with PostgreSQLDumper(
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=config.password
        ) as dumper:
            
            # Obtener información de la base de datos
            print("📊 Obteniendo información de la base de datos...")
            info = dumper.get_database_info()
            
            if info:
                print(f"✅ Conectado a: {info['database']}")
                print(f"   Servidor: {info['server_host']}:{info['server_port']}")
                print(f"   Usuario: {info['user']}")
                print(f"   Tamaño: {info['size']}")
                print(f"   Versión: {info['version']}")
            else:
                print("❌ No se pudo obtener información de la base de datos")
                return
            
            # Crear directorio de dumps si no existe
            config.create_dump_directory()
            
            # Crear dump completo
            print("\n💾 Creando dump completo...")
            success = dumper.create_dump(compress=True)
            
            if success:
                print("✅ Dump completado exitosamente")
            else:
                print("❌ Error al crear el dump")
                
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def example_multiple_formats():
    """Ejemplo usando diferentes formatos de dump"""
    print("\n=== Ejemplo de Múltiples Formatos ===")
    
    config = DEFAULT_CONFIG
    
    if not config.validate():
        print("❌ Configuración incompleta.")
        return
    
    try:
        with PostgreSQLDumper(
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=config.password
        ) as dumper:
            
            config.create_dump_directory()
            
            # Dump SQL comprimido
            print("📦 Creando dump SQL comprimido...")
            success1 = dumper.create_dump(
                output_file=os.path.join(config.dump_output_dir, "ejemplo_comprimido.sql.gz"),
                compress=True
            )
            print(f"   Resultado: {'✅ Éxito' if success1 else '❌ Error'}")
            
            # Dump SQL sin comprimir
            print("📄 Creando dump SQL sin comprimir...")
            success2 = dumper.create_dump(
                output_file=os.path.join(config.dump_output_dir, "ejemplo_sin_comprimir.sql"),
                compress=False
            )
            print(f"   Resultado: {'✅ Éxito' if success2 else '❌ Error'}")
            
            # Dump formato personalizado
            print("🔧 Creando dump formato personalizado...")
            success3 = dumper.create_custom_dump(
                output_file=os.path.join(config.dump_output_dir, "ejemplo_personalizado.dump")
            )
            print(f"   Resultado: {'✅ Éxito' if success3 else '❌ Error'}")
            
            # Solo esquema
            print("🏗️  Creando dump solo esquema...")
            success4 = dumper.create_dump(
                output_file=os.path.join(config.dump_output_dir, "ejemplo_solo_esquema.sql"),
                schema_only=True,
                compress=False
            )
            print(f"   Resultado: {'✅ Éxito' if success4 else '❌ Error'}")
            
            # Solo datos
            print("📊 Creando dump solo datos...")
            success5 = dumper.create_dump(
                output_file=os.path.join(config.dump_output_dir, "ejemplo_solo_datos.sql"),
                data_only=True,
                compress=False
            )
            print(f"   Resultado: {'✅ Éxito' if success5 else '❌ Error'}")
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def example_restore():
    """Ejemplo de restauración de dump"""
    print("\n=== Ejemplo de Restauración ===")
    
    config = DEFAULT_CONFIG
    
    if not config.validate():
        print("❌ Configuración incompleta.")
        return
    
    # Buscar archivos de dump en el directorio
    dump_dir = config.dump_output_dir
    if not os.path.exists(dump_dir):
        print(f"❌ Directorio de dumps no existe: {dump_dir}")
        return
    
    dump_files = [f for f in os.listdir(dump_dir) if f.endswith(('.sql', '.dump', '.gz'))]
    
    if not dump_files:
        print("❌ No se encontraron archivos de dump para restaurar")
        return
    
    print(f"📁 Archivos de dump encontrados: {len(dump_files)}")
    for file in dump_files[:3]:  # Mostrar solo los primeros 3
        print(f"   - {file}")
    
    # Nota: En un ejemplo real, no restauraríamos automáticamente
    print("\n⚠️  Nota: La restauración real requiere una base de datos de destino apropiada")
    print("   Ejemplo de comando para restaurar:")
    print(f"   python main.py restore {dump_files[0]}")


def main():
    """Función principal del ejemplo"""
    print("🐘 PostgreSQL Dumper - Ejemplos de Uso")
    print("=" * 50)
    
    # Verificar si existe archivo .env
    if not os.path.exists('.env'):
        print("❌ No se encontró archivo .env")
        print("💡 Ejecuta: python main.py setup")
        return
    
    # Ejecutar ejemplos
    example_basic_usage()
    example_multiple_formats()
    example_restore()
    
    print("\n🎉 Ejemplos completados!")
    print("\n📝 Próximos pasos:")
    print("1. Revisa los archivos generados en el directorio 'dumps/'")
    print("2. Usa 'python main.py --help' para ver todos los comandos disponibles")
    print("3. Consulta el README.md para más información")


if __name__ == "__main__":
    main()
