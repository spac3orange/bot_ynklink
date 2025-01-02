from sqlalchemy import Column, Integer, String
from app.crud.session import  Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subscription = Column(String, index=True, default=None)
    sub_start_date = Column(String, default=None)
    sub_end_date = Column(String, index=True, default=None)

    def __repr__(self):
        return f"<User(name={self.name}, id={self.id})>"