from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType

from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    email = Column(String(120), unique=True)
    password_hash = Column(String(128), nullable=True)
    is_staff = Column(Boolean, default=0)
    is_active = Column(Boolean, default=0)

    orders = relationship('Order', back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Order(Base):

    ORDER_STATUSES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    PIZZA_SIZES = (
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('extra_large', 'Extra Large'),
    )

    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, default=0)
    order_status = Column(ChoiceType(choices=ORDER_STATUSES), default='pending')
    pizza_sizes = Column(ChoiceType(choices=PIZZA_SIZES), default='small')

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='orders')

    def __repr__(self):
        return '<Order {}>'.format(self.id)