from datetime import datetime
from sqlalchemy import Integer, String, Boolean, TIMESTAMP, ForeignKey, Float
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    ...


class Category(Base):

    __tablename__ = 'category'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.now())
    products = relationship('Product', back_populates='category', cascade='delete,all')

    def __str__(self):
        return self.name


class Product(Base):

    __tablename__ = 'product'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.now())
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'))
    category = relationship(Category, back_populates='products')
    orders = relationship('Order', back_populates='product', cascade='delete,all')

    def __str__(self):
        return f'{self.name}-{self.title}-{self.price}'


class Order(Base):

    __tablename__ = 'order'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id'))
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product = relationship(Product, back_populates='orders')

    def __str__(self):
        return f'{self.quantity}-{self.data}'