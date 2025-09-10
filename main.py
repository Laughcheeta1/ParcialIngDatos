from database import create_tables, drop_tables
from scraper import perform_scraping
from etl import (
    transfer_data_to_analytical, 
    create_analytical_tables,
    drop_analytical_tables,
    show_analytical_statistics
)


def initialize_database():
    """Inicializar la base de datos con tablas"""
    print("Creando tablas en la base de datos...")
    create_tables()
    print("Tablas creadas exitosamente!")


def initialize_analytical_database():
    """Inicializar la base de datos analítica"""
    print("Creando tablas en la base de datos analítica...")
    create_analytical_tables()
    print("Tablas analíticas creadas exitosamente!")


def main():
    print("\n" + "=" * 50)
    print("SISTEMA DE GESTIÓN DE BIBLIOTECA")
    print("=" * 50)
    print("\n--- Base de Datos Transaccional ---")
    print("1. Inicializar base de datos transaccional")
    print("2. Ejecutar web scraper")
    print("\n--- ETL y Base de Datos Analítica ---")
    print("3. Inicializar base de datos analítica")
    print("4. Transferir datos (ETL)")
    print("5. Ver estadísticas analíticas")
    print("\n6. Salir")

    option = input("\nSeleccione una opción: ").strip()
    
    if option == "1":
        confirm = input("¿Esto eliminará todos los datos existentes. Continuar? (s/n): ")
        if confirm.lower() == 's':
            drop_tables()
            initialize_database()
    elif option == "2":
        perform_scraping()
    elif option == "3":
        confirm = input("¿Esto eliminará todos los datos analíticos existentes. Continuar? (s/n): ")
        if confirm.lower() == 's':
            drop_analytical_tables()
            initialize_analytical_database()
    elif option == "4":
        print("\nIniciando proceso ETL...")
        print("Transfiriendo datos de base transaccional a analítica...")
        transfer_data_to_analytical()
    elif option == "5":
        show_analytical_statistics()
    elif option == "6":
        print("\n¡Hasta luego!")
        return
    else:
        print("\nOpción no válida. Por favor intente de nuevo.")
    
    # Ask if user wants to continue
    if input("\n¿Desea realizar otra operación? (s/n): ").lower() == 's':
        main()


if __name__ == "__main__":
    main()