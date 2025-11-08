from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class AdminResponse(Base):
    __tablename__ = "admin_responses"
    id = Column(Integer, primary_key=True)
    message = Column(String(1000))
    date_responded = Column(DateTime(timezone=True), server_default=func.now())

    admin_id = Column(Integer, ForeignKey("users.id"))
    problem_id = Column(Integer, ForeignKey("problems.id"))

    admin = relationship("User", back_populates="responses")
    problem = relationship("Problem", back_populates="response")