from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True, nullable=False)
    district = Column(String, nullable=False)
    item = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    source = Column(String, nullable=False)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now())


class LaborRate(Base):
    __tablename__ = "labor_rates"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True, nullable=False)
    district = Column(String, index=True, nullable=False)
    trade = Column(String, nullable=False)
    rate = Column(Numeric, nullable=False)
    source = Column(String, nullable=False)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now())


class LandPrice(Base):
    __tablename__ = "land_prices"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True, nullable=False)
    district = Column(String, index=True, nullable=False)
    price = Column(Numeric, nullable=False)
    source = Column(String, nullable=False)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Permit(Base):
    __tablename__ = "permits"
    id = Column(Integer, primary_key=True, index=True)
    region = Column(String, index=True, nullable=False)
    district = Column(String, index=True, nullable=False)
    fee_type = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    source = Column(String, nullable=False)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now())


class Estimate(Base):
    __tablename__ = "estimates"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_input = Column(JSON, nullable=False)
    itemized = Column(JSON, nullable=False)
    total = Column(Numeric, nullable=False)
    confidence = Column(String, nullable=False)
    time = Column(TIMESTAMP(timezone=True), server_default=func.now())

    feedback = relationship("Feedback", back_populates="estimate")
    user = relationship("User", back_populates="estimates")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    saved_estimates = relationship("SavedEstimate", back_populates="user")
    estimates = relationship("Estimate", back_populates="user")


class SavedEstimate(Base):
    __tablename__ = "saved_estimates"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    estimate = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="saved_estimates")


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    estimate_id = Column(Integer, ForeignKey("estimates.id"), nullable=False)
    actual_cost = Column(Numeric, nullable=False)
    notes = Column(String)
    submitted_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    estimate = relationship("Estimate", back_populates="feedback")
