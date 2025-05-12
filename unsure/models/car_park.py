# WSAA-project: Web Services and Applications.
# This model maps to the 'carparkdetails' table in the MySQL database.
# Author: Laura Lyons

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class CarPark(Base):
    """Database model for car park records."""
    __tablename__ = "carparkdetails"  # Matches MySQL table name

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    height = Column(Float, nullable=False)

    def __repr__(self):
        return "<CarPark(name='%s', height=%s)>" % (self.name, self.height)
