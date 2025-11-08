from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True)
    title = Column(String(250))
    description = Column(String(1000))
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    image_url = Column(String(250), nullable=True)
    status = Column(String(250), default="В обробці")

    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # адміністратор, що взяв у роботу

    user = relationship("User", foreign_keys=[user_id], back_populates="problems")
    admin = relationship("User", foreign_keys=[admin_id],back_populates="assigned_problems")

    response = relationship("AdminResponse", back_populates="problem", uselist=False)
    service_record = relationship("ServiceRecord", back_populates="problem", uselist=False)
