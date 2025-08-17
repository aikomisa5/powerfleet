from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, DB_SECRET_KEY
from .encrypted_string import EncryptedString


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)


class Brand(Base):
    __tablename__ = "brand"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # 🔗 relationship hacia Car
    cars = relationship("Car", back_populates="brand")

class Car(Base):
    __tablename__ = "car"

    id = Column(Integer, primary_key=True, index=True)
    id_brand = Column(Integer, ForeignKey("brand.id"), nullable=False)
    model = Column(String, unique=True, index=False, nullable=False)

   # 🔗 relationship hacia Brand
    brand = relationship("Brand", back_populates="cars")

    # 🔗 relationship hacia Picture
    pictures = relationship("Picture", back_populates="car")

class Picture(Base):
    __tablename__ = "picture"

    id = Column(Integer, primary_key=True, index=True)
    id_car = Column(Integer, ForeignKey("car.id"), nullable=False)
    description = Column(EncryptedString(key=DB_SECRET_KEY))
    url = Column(EncryptedString(key=DB_SECRET_KEY))

   # 🔗 relationship hacia Brand
    car = relationship("Car", back_populates="pictures")
