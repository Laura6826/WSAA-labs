# WSAA-project: Web Services and Applications.
# REST-SERVER for Air Quality Emissions
# Author: Laura Lyons

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# SQLAlchemy base and engine
Base = declarative_base()
engine = create_engine('sqlite:///air_quality.db')  # Replace with your database URI
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

# Define the AirQuality model
class AirQuality(Base):
    __tablename__ = 'air_quality'
    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(100), nullable=False)  # Location name
    pollutant = Column(String(50), nullable=False)  # Pollutant type: PM10, PM2.5, NOx, SOx
    concentration = Column(Float, nullable=False)  # Pollutant concentration in µg/m³
    timestamp = Column(DateTime, default=datetime.utcnow)  # Time of measurement

# Create the tables in the database (if not already created)
Base.metadata.create_all(engine)

# DAO class for managing Air Quality data
class AirQualityDAO:
    def __init__(self):
        self.session = session

    def create_air_quality(self, location, pollutant, concentration, timestamp=None):
        """Create a new air quality record."""
        if timestamp is None:
            timestamp = datetime.utcnow()
        new_entry = AirQuality(
            location=location,
            pollutant=pollutant,
            concentration=concentration,
            timestamp=timestamp
        )
        self.session.add(new_entry)
        self.session.commit()
        return new_entry.id

    def get_all_air_quality(self):
        """Retrieve all air quality records."""
        return self.session.query(AirQuality).all()

    def get_air_quality_by_id(self, record_id):
        """Retrieve an air quality record by ID."""
        return self.session.query(AirQuality).get(record_id)

    def update_air_quality(self, record_id, data):
        """Update an existing air quality record."""
        record = self.get_air_quality_by_id(record_id)
        if not record:
            return None
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        self.session.commit()
        return record

    def delete_air_quality(self, record_id):
        """Delete an air quality record by ID."""
        record = self.get_air_quality_by_id(record_id)
        if not record:
            return None
        self.session.delete(record)
        self.session.commit()
        return record

    def bulk_create_air_quality(self, data_list):
        """Insert multiple records into the Air Quality table."""
        for data in data_list:
            new_entry = AirQuality(
                location=data['location'],
                pollutant=data['pollutant'],
                concentration=data['concentration'],
                timestamp=data['timestamp']
            )
            self.session.add(new_entry)
        self.session.commit()
