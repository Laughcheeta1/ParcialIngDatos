from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Float

"""
Transactional models
"""
class Category(SQLModel, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    
    books: List["Book"] = Relationship(back_populates="category")


class Stock(SQLModel, table=True):
    __tablename__ = "stocks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", unique=True)
    quantity: int = Field(default=0)
    
    book: Optional["Book"] = Relationship(back_populates="stock")


class Scores(SQLModel, table=True):
    __tablename__ = "scores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", unique=True)
    score: float = Field(sa_column=Column(Float))
    
    book: Optional["Book"] = Relationship(back_populates="scores")


class Book(SQLModel, table=True):
    __tablename__ = "books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    upc: str = Field(index=True, unique=True)
    title: str = Field(index=True)
    price: float = Field(sa_column=Column(Float))
    stock_int: int = Field(default=0)
    image_url: str
    category_id: int = Field(foreign_key="categories.id")
    image_url_string: str
    description: str
    
    category: Optional[Category] = Relationship(back_populates="books")
    stock: Optional[Stock] = Relationship(
        back_populates="book", 
        sa_relationship_kwargs={"uselist": False}
    )
    scores: Optional[Scores] = Relationship(
        back_populates="book",
        sa_relationship_kwargs={"uselist": False}
    )


class TaxRate(SQLModel, table=True):
    __tablename__ = "tax_rates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tax_float: float = Field(sa_column=Column(Float), default=0.0)
    date: datetime = Field(default_factory=datetime.now())


"""
Analytical models
"""
class Tax(SQLModel, table=True):
    id: int = Field(primary_key=True)
    tax_rate: float
    date: datetime
    
    # Relationship to Price
    prices: List["Price"] = Relationship(back_populates="tax")


class Category(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    
    # Relationship to Book
    books: List["Book"] = Relationship(back_populates="category")


class Stock(SQLModel, table=True):
    id: int = Field(primary_key=True)
    quantity: int
    
    # Relationship to Book
    books: List["Book"] = Relationship(back_populates="stock")


class Scores(SQLModel, table=True):
    id: int = Field(primary_key=True)
    score: int
    
    # Relationship to Book
    books: List["Book"] = Relationship(back_populates="scores")


class Price(SQLModel, table=True):
    id: int = Field(primary_key=True)
    tax_id: int = Field(foreign_key="tax.id")
    price_before_tax: float
    price_after_tax: float
    
    # Relationships
    tax: Tax = Relationship(back_populates="prices")
    books: List["Book"] = Relationship(back_populates="price")


class Book(SQLModel, table=True):
    """Central fact table in the snowflake schema"""
    id: int = Field(primary_key=True)
    upc: str
    title: str
    price_id: int = Field(foreign_key="price.id")
    stock_id: int = Field(foreign_key="stock.id")
    image_url: str
    category_id: int = Field(foreign_key="category.id")
    score_id: int = Field(foreign_key="scores.id")
    description: str
    
    # Relationships
    price: Price = Relationship(back_populates="books")
    stock: Stock = Relationship(back_populates="books")
    category: Category = Relationship(back_populates="books")
    scores: Scores = Relationship(back_populates="books")