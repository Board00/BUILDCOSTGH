from sqlalchemy import Column, Integer, String, Numeric, Date, TIMESTAMP, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    item = Column(String)
    unit = Column(String)
    price = Column(Numeric)
    region = Column(String, index=True)
    source = Column(String)
    date = Column(TIMESTAMP, server_default=func.now(), default=func.now())

class LaborRate(Base):
    __tablename__ = "labor_rates"
    id = Column(Integer, primary_key=True, index=True)
    trade = Column(String)
    rate = Column(Numeric)
    region = Column(String, index=True)
    source = Column(String)
    date = Column(TIMESTAMP, server_default=func.now(), default=func.now())

class LandPrice(Base):
    __tablename__ = "land_prices"
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String)
    price = Column(Numeric)
    source = Column(String)
    date = Column(TIMESTAMP, server_default=func.now(), default=func.now())

class Permit(Base):
    __tablename__ = "permits"
    id = Column(Integer, primary_key=True, index=True)
    fee_type = Column(String)
    amount = Column(Numeric)
    region = Column(String, index=True)
    source = Column(String)
    date = Column(TIMESTAMP, server_default=func.now(), default=func.now())

class Estimate(Base):
    __tablename__ = "estimates"
    id = Column(Integer, primary_key=True, index=True)
    user_input = Column(JSON)
    itemized = Column(JSON)
    total = Column(Numeric)
    confidence = Column(String)
    date = Column(TIMESTAMP, server_default=func.now())


    feedback = relationship("Feedback", back_populates="estimate")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)  # ✅ new field
    created_at = Column(TIMESTAMP, server_default=func.now())

    saved_estimates = relationship("SavedEstimate", back_populates="user")

class SavedEstimate(Base):
    __tablename__ = "saved_estimates"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    estimate = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="saved_estimates")

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey("estimates.id"))
    actual_cost = Column(Numeric)
    notes = Column(String)
    submitted_at = Column(TIMESTAMP, server_default=func.now())

    estimate = relationship("Estimate", back_populates="feedback")
