from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class ProduceInventory(Base):
    """ Produce Item """

    __tablename__ = "ProduceItem"

    reading_id = Column(Integer, primary_key=True)
    id = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    supplier = Column(String(250), nullable=False)
    price = Column(String(100), nullable=False)
    expiration_date = Column(String(250), nullable=False)
    weight = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=True)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, id, name, supplier, price, expiration_date, weight, quantity):
        """ Initializes a produce item reading """
        self.id = id
        self.name = name
        self.supplier = supplier
        self.price = price
        self.expiration_date = expiration_date
        self.weight = weight
        self.quantity = quantity
        self.date_created = datetime.datetime.now()  # Sets the date/time record is created


    def to_dict(self):
        """ Dictionary Representation of a produce item """
        dict = {}
        dict['reading_id'] = self.reading_id
        dict['id'] = self.id
        dict['name'] = self.name
        dict['supplier'] = self.supplier
        dict['price'] = self.price
        dict['expiration_date'] = self.expiration_date
        dict['weight'] = self.weight
        dict['quantity'] = self.quantity
        dict['date_created'] = self.date_created

        return dict
