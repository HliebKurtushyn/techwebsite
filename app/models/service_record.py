from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class ServiceRecord(Base):
    __tablename__ = "service_records"
    id = Column(Integer, primary_key=True)
    work_done = Column(String(1000))
    date_completed = Column(DateTime(timezone=True), server_default=func.now())
    parts_used = Column(String(1000), nullable=True)  # можеш пізніше зробити окрему таблицю
    warranty_info = Column(String(1000))

    problem_id = Column(Integer, ForeignKey("problems.id"))

    problem = relationship("Problem", back_populates="service_record")