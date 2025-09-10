from sqlmodel import Session, select, func
from models_analytical import FactBook, DimCategory, DimStock, DimPrice
from etl import analytical_engine
from typing import Dict, List, Tuple


def contar_categorias() -> int:
    """a. ¿Cuántas categorías de libros se tienen?"""
    with Session(analytical_engine) as session:
        count = session.exec(
            select(func.count(DimCategory.id))
        ).first()
        return count


def libros_por_categoria() -> Dict[str, int]:
    """b. ¿Cuántos libros hay por categoría?"""
    with Session(analytical_engine) as session:
        results = session.exec(
            select(DimCategory.name, func.count(FactBook.id))
            .join(FactBook, FactBook.category_id == DimCategory.id)
            .group_by(DimCategory.name)
            .order_by(DimCategory.name)
        ).all()
        return {categoria: cantidad for categoria, cantidad in results}


def libro_mas_caro() -> Dict:
    """c. ¿Cuál es el libro más caro?"""
    with Session(analytical_engine) as session:
        result = session.exec(
            select(FactBook, DimPrice, DimCategory)
            .join(DimPrice, FactBook.price_id == DimPrice.id)
            .join(DimCategory, FactBook.category_id == DimCategory.id)
            .order_by(DimPrice.price_before_tax.desc())
            .limit(1)
        ).first()
        
        if result:
            book, price, category = result
            return {
                "titulo": book.title,
                "precio": price.price_before_tax,
                "categoria": category.name,
                "upc": book.upc
            }
        return None


def libros_en_multiples_categorias() -> List[Dict]:
    """d. ¿Hay algún libro que esté en dos categorías?"""
    with Session(analytical_engine) as session:
        # Buscar libros con el mismo título en diferentes categorías
        subquery = (
            select(FactBook.title, func.count(func.distinct(FactBook.category_id)).label("num_categorias"))
            .group_by(FactBook.title)
            .having(func.count(func.distinct(FactBook.category_id)) > 1)
            .subquery()
        )
        
        results = session.exec(
            select(FactBook, DimCategory)
            .join(DimCategory, FactBook.category_id == DimCategory.id)
            .join(subquery, FactBook.title == subquery.c.title)
            .order_by(FactBook.title, DimCategory.name)
        ).all()
        
        # Agrupar por título
        libros_duplicados = {}
        for book, category in results:
            if book.title not in libros_duplicados:
                libros_duplicados[book.title] = []
            libros_duplicados[book.title].append(category.name)
        
        return [{"titulo": titulo, "categorias": categorias} 
                for titulo, categorias in libros_duplicados.items()]


def libro_mas_barato_por_categoria() -> Dict[str, List[Dict]]:
    """e. ¿Cuál es el libro más barato por categoría? Si es más de uno, se deben mostrar."""
    with Session(analytical_engine) as session:
        # Primero obtener el precio mínimo por categoría
        min_prices = session.exec(
            select(DimCategory.id, func.min(DimPrice.price_before_tax).label("min_price"))
            .join(FactBook, FactBook.category_id == DimCategory.id)
            .join(DimPrice, FactBook.price_id == DimPrice.id)
            .group_by(DimCategory.id)
        ).all()
        
        resultado = {}
        for cat_id, min_price in min_prices:
            # Obtener todos los libros con ese precio mínimo en esa categoría
            books = session.exec(
                select(FactBook, DimCategory, DimPrice)
                .join(DimCategory, FactBook.category_id == DimCategory.id)
                .join(DimPrice, FactBook.price_id == DimPrice.id)
                .where(DimCategory.id == cat_id)
                .where(DimPrice.price_before_tax == min_price)
            ).all()
            
            for book, category, price in books:
                if category.name not in resultado:
                    resultado[category.name] = []
                resultado[category.name].append({
                    "titulo": book.title,
                    "precio": price.price_before_tax,
                    "upc": book.upc
                })
        
        return resultado


def diferencia_vs_promedio_categoria() -> List[Dict]:
    """f. ¿Cuánto más caro o barato es cada libro respecto al promedio de su categoría?"""
    with Session(analytical_engine) as session:
        # Calcular promedio por categoría
        avg_prices = session.exec(
            select(DimCategory.id, func.avg(DimPrice.price_before_tax).label("avg_price"))
            .join(FactBook, FactBook.category_id == DimCategory.id)
            .join(DimPrice, FactBook.price_id == DimPrice.id)
            .group_by(DimCategory.id)
        ).all()
        
        avg_dict = {cat_id: float(avg_price) for cat_id, avg_price in avg_prices}
        
        # Obtener todos los libros con sus precios
        books = session.exec(
            select(FactBook, DimCategory, DimPrice)
            .join(DimCategory, FactBook.category_id == DimCategory.id)
            .join(DimPrice, FactBook.price_id == DimPrice.id)
            .order_by(DimCategory.name, FactBook.title)
        ).all()
        
        resultado = []
        for book, category, price in books:
            avg_price = avg_dict.get(category.id, 0)
            diferencia = price.price_before_tax - avg_price
            porcentaje = (diferencia / avg_price * 100) if avg_price > 0 else 0
            
            resultado.append({
                "titulo": book.title,
                "categoria": category.name,
                "precio": price.price_before_tax,
                "promedio_categoria": round(avg_price, 2),
                "diferencia": round(diferencia, 2),
                "porcentaje_diferencia": round(porcentaje, 2),
                "estado": "más caro" if diferencia > 0 else "más barato" if diferencia < 0 else "igual"
            })
        
        return resultado


def libro_mayor_ingreso_por_categoria() -> Dict[str, Dict]:
    """g. Asumiendo que se venden todos los libros que están en stock en este momento
    ¿Cuál es el libro que daría más ingresos por categoría?"""
    with Session(analytical_engine) as session:
        # Calcular ingresos potenciales (precio * stock)
        results = session.exec(
            select(
                FactBook,
                DimCategory,
                DimPrice,
                DimStock,
                (DimPrice.price_before_tax * DimStock.quantity).label("ingreso_potencial")
            )
            .join(DimCategory, FactBook.category_id == DimCategory.id)
            .join(DimPrice, FactBook.price_id == DimPrice.id)
            .join(DimStock, FactBook.stock_id == DimStock.id)
            .order_by(DimCategory.name, (DimPrice.price_before_tax * DimStock.quantity).desc())
        ).all()
        
        # Agrupar por categoría y obtener el de mayor ingreso
        resultado = {}
        categorias_vistas = set()
        
        for book, category, price, stock, ingreso in results:
            if category.name not in categorias_vistas:
                resultado[category.name] = {
                    "titulo": book.title,
                    "precio": price.price_before_tax,
                    "stock": stock.quantity,
                    "ingreso_potencial": round(ingreso, 2),
                    "upc": book.upc
                }
                categorias_vistas.add(category.name)
        
        return resultado


def ejecutar_analisis():
    """Ejecuta todos los análisis y muestra los resultados"""
    print("=" * 80)
    print("ANÁLISIS DE LA BASE DE DATOS DE LIBROS")
    print("=" * 80)
    
    # a. Contar categorías
    print("\na. ¿Cuántas categorías de libros se tienen?")
    print("-" * 40)
    num_categorias = contar_categorias()
    print(f"Total de categorías: {num_categorias}")
    
    # b. Libros por categoría
    print("\nb. ¿Cuántos libros hay por categoría?")
    print("-" * 40)
    libros_categoria = libros_por_categoria()
    for categoria, cantidad in libros_categoria.items():
        print(f"{categoria}: {cantidad} libros")
    print(f"Total de libros: {sum(libros_categoria.values())}")
    
    # c. Libro más caro
    print("\nc. ¿Cuál es el libro más caro?")
    print("-" * 40)
    mas_caro = libro_mas_caro()
    if mas_caro:
        print(f"Título: {mas_caro['titulo']}")
        print(f"Precio: ${mas_caro['precio']:.2f}")
        print(f"Categoría: {mas_caro['categoria']}")
        print(f"UPC: {mas_caro['upc']}")
    
    # d. Libros en múltiples categorías
    print("\nd. ¿Hay algún libro que esté en dos categorías?")
    print("-" * 40)
    duplicados = libros_en_multiples_categorias()
    if duplicados:
        for libro in duplicados:
            print(f"Título: {libro['titulo']}")
            print(f"Categorías: {', '.join(libro['categorias'])}")
            print()
    else:
        print("No hay libros que estén en múltiples categorías")
    
    # e. Libro más barato por categoría
    print("\ne. ¿Cuál es el libro más barato por categoría?")
    print("-" * 40)
    mas_baratos = libro_mas_barato_por_categoria()
    for categoria, libros in sorted(mas_baratos.items()):
        print(f"\n{categoria}:")
        for libro in libros:
            print(f"  - {libro['titulo']} (${libro['precio']:.2f})")
    
    # f. Diferencia vs promedio
    print("\nf. ¿Cuánto más caro o barato es cada libro respecto al promedio de su categoría?")
    print("-" * 40)
    diferencias = diferencia_vs_promedio_categoria()
    
    # Mostrar solo los 5 más caros y 5 más baratos respecto al promedio
    diferencias_ordenadas = sorted(diferencias, key=lambda x: x['diferencia'])
    
    print("\n5 Libros más baratos respecto al promedio de su categoría:")
    for libro in diferencias_ordenadas[:5]:
        print(f"  {libro['titulo'][:50]}")
        print(f"    Categoría: {libro['categoria']}")
        print(f"    Precio: ${libro['precio']:.2f} | Promedio: ${libro['promedio_categoria']:.2f}")
        print(f"    Diferencia: ${libro['diferencia']:.2f} ({libro['porcentaje_diferencia']:.1f}%)")
        print()
    
    print("\n5 Libros más caros respecto al promedio de su categoría:")
    for libro in diferencias_ordenadas[-5:]:
        print(f"  {libro['titulo'][:50]}")
        print(f"    Categoría: {libro['categoria']}")
        print(f"    Precio: ${libro['precio']:.2f} | Promedio: ${libro['promedio_categoria']:.2f}")
        print(f"    Diferencia: ${libro['diferencia']:.2f} ({libro['porcentaje_diferencia']:.1f}%)")
        print()
    
    # g. Mayor ingreso por categoría
    print("\ng. ¿Cuál es el libro que daría más ingresos por categoría?")
    print("-" * 40)
    mayores_ingresos = libro_mayor_ingreso_por_categoria()
    for categoria, libro in sorted(mayores_ingresos.items()):
        print(f"\n{categoria}:")
        print(f"  Título: {libro['titulo'][:50]}")
        print(f"  Precio: ${libro['precio']:.2f}")
        print(f"  Stock: {libro['stock']} unidades")
        print(f"  Ingreso potencial: ${libro['ingreso_potencial']:.2f}")
    
    print("\n" + "=" * 80)
    print("FIN DEL ANÁLISIS")
    print("=" * 80)


if __name__ == "__main__":
    try:
        ejecutar_analisis()
    except Exception as e:
        print(f"Error al ejecutar el análisis: {e}")
        print("\nAsegúrate de que:")
        print("1. La base de datos analítica esté configurada correctamente")
        print("2. Se haya ejecutado el proceso ETL para poblar las tablas analíticas")
        print("3. Las variables de entorno estén configuradas correctamente")