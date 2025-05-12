# WSAA-project: Web Services and Applications.
# This model maps to the 'openinghours' table in the MySQL database.
# Author: Laura Lyons

from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OpeningHours(Base):
    """Database model for opening hours, mapping to the 'openinghours' table."""
    __tablename__ = "openinghours"  # Matches MySQL table name

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_park_id = Column(Integer, ForeignKey("carparkdetails.id"), nullable=False)  # Matches car parks table
    day = Column(String(10), nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    status = Column(String(20), nullable=True)  # Optional field

    def __repr__(self):
        return "<OpeningHours(car_park_id=%s, day='%s', opening='%s', closing='%s', status='%s')>" % (
            self.car_park_id, self.day, self.opening_time, self.closing_time, self.status
        )

