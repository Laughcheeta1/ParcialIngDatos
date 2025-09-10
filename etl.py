from sqlmodel import Session, select, create_engine
from models_transactional import Book, TaxRate
from models_analytical import (
    FactBook, DimCategory, DimStock, DimScore, DimPrice, DimTax,
    analytical_metadata
)
from database import engine as transactional_engine
from datetime import datetime
import os


# Analytical database connection
ANALYTICAL_DB_URL = os.getenv(
    "ANALYTICAL_DATABASE_URL",
    "postgresql://user:password@localhost:5432/biblioteca_analytical"
)

analytical_engine = create_engine(
    ANALYTICAL_DB_URL,
    echo=False,
    pool_pre_ping=True
)


def create_analytical_tables():
    """Create all analytical tables in the analytical database"""
    analytical_metadata.create_all(analytical_engine)


def drop_analytical_tables():
    """Drop all analytical tables from the analytical database"""
    analytical_metadata.drop_all(analytical_engine)


def get_or_create_dimension(session, model_class, **kwargs):
    """Helper function to get or create a dimension record"""
    # Try to find existing record
    query = select(model_class)
    for key, value in kwargs.items():
        query = query.where(getattr(model_class, key) == value)
    
    existing = session.exec(query).first()
    if existing:
        return existing
    
    # Create new record
    new_record = model_class(**kwargs)
    session.add(new_record)
    session.flush()  # Flush to get the ID without committing
    return new_record


def classify_stock_status(quantity: int) -> str:
    """Classify stock status based on quantity"""
    if quantity == 0:
        return "Out of Stock"
    elif quantity < 10:
        return "Low Stock"
    else:
        return "In Stock"


def classify_rating(score: float) -> str:
    """Classify rating based on score"""
    if score >= 4.5:
        return "Excellent"
    elif score >= 3.5:
        return "Good"
    elif score >= 2.5:
        return "Average"
    else:
        return "Poor"


def classify_price_range(price: float) -> str:
    """Classify price range"""
    if price < 20:
        return "Budget"
    elif price < 50:
        return "Mid-range"
    else:
        return "Premium"


def transfer_data_to_analytical():
    """
    Extract data from transactional database,
    Transform it according to the snowflake schema,
    Load it into the analytical database
    """
    print("\n" + "="*50)
    print("Starting ETL Process")
    print("="*50)
    
    with Session(transactional_engine) as trans_session:
        with Session(analytical_engine) as anal_session:
            
            # 1. Extract all books from transactional database
            books = trans_session.exec(select(Book)).all()
            total_books = len(books)
            print(f"\nFound {total_books} books to transfer")
            
            # 2. Get the latest tax rate
            latest_tax = trans_session.exec(
                select(TaxRate).order_by(TaxRate.date.desc())
            ).first()
            
            if not latest_tax:
                print("Warning: No tax rate found, using default 0.0")
                latest_tax = TaxRate(tax_float=0.0, date=datetime.now())
            
            # 3. Create or get Tax dimension
            dim_tax = get_or_create_dimension(
                anal_session,
                DimTax,
                tax_rate=latest_tax.tax_float,
                date=latest_tax.date
            )
            
            # 4. Process each book
            transferred = 0
            skipped = 0
            
            for book in books:
                try:
                    # Check if book already exists in analytical DB
                    existing_fact = anal_session.exec(
                        select(FactBook).where(FactBook.upc == book.upc)
                    ).first()
                    
                    if existing_fact:
                        print(f"Skipping {book.title} - already exists")
                        skipped += 1
                        continue
                    
                    # Create Category dimension
                    dim_category = None
                    if book.category:
                        dim_category = get_or_create_dimension(
                            anal_session,
                            DimCategory,
                            name=book.category.name
                        )
                    
                    # Create Stock dimension
                    dim_stock = None
                    if book.stock:
                        stock_status = classify_stock_status(book.stock.quantity)
                        dim_stock = get_or_create_dimension(
                            anal_session,
                            DimStock,
                            quantity=book.stock.quantity,
                            stock_status=stock_status
                        )
                    elif book.stock_int:
                        stock_status = classify_stock_status(book.stock_int)
                        dim_stock = get_or_create_dimension(
                            anal_session,
                            DimStock,
                            quantity=book.stock_int,
                            stock_status=stock_status
                        )
                    
                    # Create Score dimension
                    dim_score = None
                    if book.scores:
                        dim_score = get_or_create_dimension(
                            anal_session,
                            DimScore,
                            score=book.scores.score
                        )
                    
                    # Create Price dimension
                    price_before_tax = book.price
                    price_after_tax = price_before_tax * (1 + latest_tax.tax_float)
                    price_range = classify_price_range(price_before_tax)
                    
                    dim_price = get_or_create_dimension(
                        anal_session,
                        DimPrice,
                        price_before_tax=price_before_tax,
                        price_after_tax=price_after_tax,
                        price_range=price_range,
                        tax_id=dim_tax.id
                    )
                    
                    # Create Fact record
                    fact_book = FactBook(
                        upc=book.upc,
                        title=book.title,
                        description=book.description,
                        image_url=book.image_url,
                        category_id=dim_category.id if dim_category else None,
                        stock_id=dim_stock.id if dim_stock else None,
                        score_id=dim_score.id if dim_score else None,
                        price_id=dim_price.id
                    )
                    
                    anal_session.add(fact_book)
                    transferred += 1
                    
                    if transferred % 10 == 0:
                        print(f"Transferred {transferred}/{total_books} books...")
                        anal_session.commit()  # Commit in batches
                
                except Exception as e:
                    print(f"Error transferring book {book.title}: {e}")
                    anal_session.rollback()
                    continue
            
            # Final commit
            anal_session.commit()
            
            print("\n" + "="*50)
            print("ETL Process Complete!")
            print(f"Transferred: {transferred} books")
            print(f"Skipped (already exists): {skipped} books")
            print("="*50)
            
            # Print summary statistics
            total_facts = anal_session.exec(select(FactBook)).all()
            total_categories = anal_session.exec(select(DimCategory)).all()
            total_stocks = anal_session.exec(select(DimStock)).all()
            
            print("\nAnalytical Database Summary:")
            print(f"Total Fact Records: {len(total_facts)}")
            print(f"Total Categories: {len(total_categories)}")
            print(f"Total Stock Dimensions: {len(total_stocks)}")


def show_analytical_statistics():
    """Show statistics from the analytical database"""
    # Importar las funciones del archivo de análisis
    from analisis_libros import ejecutar_analisis
    
    try:
        # Ejecutar todas las consultas analíticas
        ejecutar_analisis()
    except Exception as e:
        print(f"\nError al ejecutar análisis: {e}")
        print("\nEjecutando estadísticas básicas como respaldo...")
        
        # Estadísticas básicas de respaldo
        with Session(analytical_engine) as session:
            total_books = len(session.exec(select(FactBook)).all())
            categories = session.exec(select(DimCategory)).all()
            
            print("\n" + "="*50)
            print("Estadísticas Básicas de la Base de Datos Analítica")
            print("="*50)
            print(f"\nTotal de Libros: {total_books}")
            print(f"Total de Categorías: {len(categories)}")
            
            if total_books == 0:
                print("\n⚠ No hay datos en la base de datos analítica.")
                print("Por favor, ejecute primero la opción 4 (Transferir datos ETL)")
