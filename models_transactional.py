from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Float, MetaData

# Create separate metadata for transactional models
transactional_metadata = MetaData()

# Base class for transactional models
class TransactionalBase(SQLModel):
    metadata = transactional_metadata


class Category(TransactionalBase, table=True):
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    
    books: List["Book"] = Relationship(back_populates="category")


class Stock(TransactionalBase, table=True):
    __tablename__ = "stocks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", unique=True)
    quantity: int = Field(default=0)
    
    book: Optional["Book"] = Relationship(back_populates="stock")


class Scores(TransactionalBase, table=True):
    __tablename__ = "scores"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="books.id", unique=True)
    score: float = Field(sa_column=Column(Float))
    
    book: Optional["Book"] = Relationship(back_populates="scores")


class Book(TransactionalBase, table=True):
    __tablename__ = "books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    upc: str = Field(index=True, unique=True)
    title: str = Field(index=True)
    price: float = Field(sa_column=Column(Float))
    stock_int: int = Field(default=0)
    image_url: str
    category_id: int = Field(foreign_key="categories.id")
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


class TaxRate(TransactionalBase, table=True):
    __tablename__ = "tax_rates"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tax_float: float = Field(sa_column=Column(Float), default=0.0)
    date: datetime = Field(default_factory=datetime.now)