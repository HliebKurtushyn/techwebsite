from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

import bcrypt

from app.db.session import Base
from app.models.problem import Problem

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    is_admin = Column(Boolean, default=False)

    problems = relationship("Problem", foreign_keys=[Problem.user_id],back_populates="user")
    assigned_problems = relationship("Problem", foreign_keys=[Problem.admin_id], back_populates="admin")
    responses = relationship("AdminResponse", back_populates="admin")

    def set_password(self, raw_password: str):
        hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
        self.password = hashed.decode("utf-8")  # зберігаємо як str

    def verify_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(raw_password.encode("utf-8"), self.password.encode("utf-8"))
