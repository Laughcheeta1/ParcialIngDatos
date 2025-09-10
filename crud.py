from typing import List, Optional
from sqlmodel import Session, select
from models_transactional import Book, Category, Stock, Scores, TaxRate
from database import get_session


def save_book_information(book_information: dict, category_name: str):
    # First save the category
    category = CategoryCRUD.create(category_name)

    book = BookCRUD.create(
        upc=book_information['upc'],
        title=book_information['title'],
        price=book_information['price'],
        category_id=category.id,
        description=book_information['description'],
        image_url=book_information['image_url'],
        stock_int=book_information['stock']
    )

    ScoreCRUD.create(book_id=book.id, quantity=book_information['stock'])
    StockCRUD.create(book_id=book.id, quantity=book_information['stock'])


class CategoryCRUD:
    @staticmethod
    def create(name: str) -> Optional[Category]:
        try:
            with get_session() as session:
                existing = session.exec(select(Category).where(Category.name == name)).first()
                if existing:
                    return existing
                category = Category(name=name)
                session.add(category)
                session.commit()
                session.refresh(category)
                return category
        except Exception as e:
            print(f"Error creating category: {e}")
            return None
   

class BookCRUD:
    @staticmethod
    def create(
        upc: str,
        title: str,
        price: float,
        category_id: int,
        description: str,
        image_url: str,
        image_url_string: str,
        stock_int: int = 0
    ) -> Optional[Book]:
        try:
            with get_session() as session:
                existing = session.exec(select(Book).where(Book.upc == upc)).first()
                if existing:
                    return existing
                    
                book = Book(
                    upc=upc,
                    title=title,
                    price=price,
                    category_id=category_id,
                    description=description,
                    image_url=image_url,
                    image_url_string=image_url_string,
                    stock_int=stock_int
                )
                session.add(book)
                session.commit()
                session.refresh(book)
                
                return book
        except Exception as e:
            print(f"Error creating book: {e}")
            return None


class StockCRUD:
    @staticmethod
    def create(book_id: int, quantity: int) -> Optional[Stock]:
        with get_session() as session:
            existing = session.exec(select(Stock).where(Stock.book_id == book_id)).first()
            if existing:
                return existing
            stock = Stock(book_id=book_id, quantity=quantity)
            session.add(stock)
            session.commit()
            session.refresh(stock)
            return stock


class ScoreCRUD:
    @staticmethod
    def create(book_id: int, score: float) -> Optional[Scores]:
        try:
            with get_session() as session:
                # Check if score already exists for this book
                existing_score = session.exec(
                    select(Scores).where(Scores.book_id == book_id)
                ).first()
                
                if existing_score:
                    print(f"Score already exists for book_id {book_id}")
                    return existing_score
                
                # Verify book exists
                book = session.get(Book, book_id)
                if not book:
                    print(f"Book with id {book_id} not found")
                    return None
                
                score_record = Scores(
                    book_id=book_id,
                    score=score
                )
                session.add(score_record)
                session.commit()
                session.refresh(score_record)
                
                return score_record
        except Exception as e:
            print(f"Error creating score: {e}")
            return None