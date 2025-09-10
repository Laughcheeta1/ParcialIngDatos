from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Float, MetaData

# Create separate metadata for analytical models
analytical_metadata = MetaData()

# Base class for analytical models
class AnalyticalBase(SQLModel):
    metadata = analytical_metadata


class DimTax(AnalyticalBase, table=True):
    __tablename__ = "dim_tax"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    tax_rate: float = Field(sa_column=Column(Float))
    date: datetime
    
    prices: List["DimPrice"] = Relationship(back_populates="tax")


class DimCategory(AnalyticalBase, table=True):
    __tablename__ = "dim_category"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    
    fact_books: List["FactBook"] = Relationship(back_populates="category")


class DimStock(AnalyticalBase, table=True):
    __tablename__ = "dim_stock"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int
    stock_status: str
    
    fact_books: List["FactBook"] = Relationship(back_populates="stock")


class DimScore(AnalyticalBase, table=True):
    __tablename__ = "dim_score"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    score: float = Field(sa_column=Column(Float))
    
    fact_books: List["FactBook"] = Relationship(back_populates="score")


class DimPrice(AnalyticalBase, table=True):
    __tablename__ = "dim_price"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    price_before_tax: float = Field(sa_column=Column(Float))
    price_after_tax: float = Field(sa_column=Column(Float))
    price_range: str
    tax_id: Optional[int] = Field(foreign_key="dim_tax.id")
    
    tax: Optional[DimTax] = Relationship(back_populates="prices")
    fact_books: List["FactBook"] = Relationship(back_populates="price")


class FactBook(AnalyticalBase, table=True):
    __tablename__ = "fact_books"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    upc: str = Field(unique=True)
    title: str
    description: str
    image_url: str

    category_id: Optional[int] = Field(foreign_key="dim_category.id")
    stock_id: Optional[int] = Field(foreign_key="dim_stock.id")
    score_id: Optional[int] = Field(foreign_key="dim_score.id")
    price_id: Optional[int] = Field(foreign_key="dim_price.id")

    category: Optional[DimCategory] = Relationship(back_populates="fact_books")
    stock: Optional[DimStock] = Relationship(back_populates="fact_books")
    score: Optional[DimScore] = Relationship(back_populates="fact_books")
    price: Optional[DimPrice] = Relationship(back_populates="fact_books")