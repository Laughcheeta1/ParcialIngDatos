#!/usr/bin/env python
"""
Script para ejecutar el proceso ETL automáticamente.
Este script:
1. Inicializa la base de datos analítica si es necesario
2. Transfiere los datos de la base transaccional a la analítica
3. Muestra estadísticas del proceso
"""

from etl import (
    transfer_data_to_analytical, 
    create_analytical_tables,
    show_analytical_statistics
)
from sqlmodel import Session, select
from models_analytical import FactBook
from etl import analytical_engine


def run_etl_process():
    """Ejecuta el proceso ETL completo"""
    
    print("\n" + "="*60)
    print("PROCESO ETL - TRANSFERENCIA A BASE DE DATOS ANALÍTICA")
    print("="*60)
    
    # Verificar si las tablas analíticas existen
    try:
        with Session(analytical_engine) as session:
            # Intenta hacer una consulta simple para verificar si las tablas existen
            session.exec(select(FactBook).limit(1)).first()
            print("\n✓ Base de datos analítica detectada")
    except Exception as e:
        print("\n⚠ Base de datos analítica no encontrada. Creando tablas...")
        create_analytical_tables()
        print("✓ Tablas analíticas creadas exitosamente")
    
    # Ejecutar transferencia de datos
    print("\n" + "-"*60)
    print("Iniciando transferencia de datos...")
    print("-"*60)
    
    transfer_data_to_analytical()
    
    # Mostrar estadísticas
    print("\n" + "-"*60)
    print("ESTADÍSTICAS FINALES")
    print("-"*60)
    
    show_analytical_statistics()
    
    print("\n" + "="*60)
    print("PROCESO ETL COMPLETADO EXITOSAMENTE")
    print("="*60)


if __name__ == "__main__":
    try:
        run_etl_process()
    except Exception as e:
        print(f"\n❌ Error durante el proceso ETL: {e}")
        print("\nPosibles causas:")
        print("1. La base de datos analítica no está configurada correctamente")
        print("2. No hay datos en la base de datos transaccional")
        print("3. Problemas de conexión con PostgreSQL")
        print("\nVerifique la configuración y vuelva a intentar.")