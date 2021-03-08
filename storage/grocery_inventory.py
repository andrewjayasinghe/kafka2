from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class GroceryInventory(Base):
    """Grocery Item"""

    __tablename__ = "GroceryItem"

    reading_id = Column(Integer, primary_key=True)
    id = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    manufacturer = Column(String(250), nullable=False)
    price = Column(String(100), nullable=False)
    manufacture_date = Column(String(100), nullable=False)
    expiration_date = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)


    def __init__(self, id, name, manufacturer, price, manufacture_date, expiration_date, quantity):
        """ Initializes a grocery item """
        self.id = id
        self.name = name
        self.manufacturer = manufacturer
        self.price = price
        self.manufacture_date = manufacture_date
        self.expiration_date = expiration_date
        self.quantity = quantity
        self.date_created = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a grocery item """
        dict = {}
        dict['id'] = self.id
        dict['name'] = self.name
        dict['manufacturer'] = self.manufacturer
        dict['price'] = self.price
        dict['manufacture_date'] = self.manufacture_date
        dict['expiration_date'] = self.expiration_date
        dict['quantity'] = self.quantity
        dict['date_created'] = self.date_created


        return dict
