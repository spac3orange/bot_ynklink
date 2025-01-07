from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
import json
from app.crud.session import  Base


def prepare_jsonb_data(data):
    """
    Преобразует данные в формат JSONB для записи в столбец media.

    :param data: Данные для преобразования (например, список, словарь).
    :return: JSON-совместимая структура.
    :raises ValueError: Если данные не могут быть сериализованы в JSON.
    """
    try:
        # Убедимся, что данные можно сериализовать в JSON
        json_data = json.dumps(data)
        # Десериализуем обратно для обеспечения совместимости с JSONB
        return json.loads(json_data)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Невозможно преобразовать данные в JSONB: {e}")


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, index=True)
    subscription = Column(String, index=True, default=None)
    sub_start_date = Column(String, default=None)
    sub_end_date = Column(String, index=True, default=None)

    def __repr__(self):
        return f"<User(name={self.name}, id={self.id})>"


class UserData(Base):
    __tablename__ = 'users_data'

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(BigInteger, index=True)
    number = Column(String, index=True)
    city = Column(String)
    document = Column(BigInteger, index=True)
    name = Column(String)
    comment = Column(String, default=None)
    media = Column(JSONB, default=[])


class TempData(Base):
    __tablename__ = 'temp_data'

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(BigInteger, index=True)
    number = Column(String, index=True)
    city = Column(String)
    document = Column(BigInteger, index=True)
    name = Column(String)
    comment = Column(String, default=None)
    media = Column(JSONB, default=[])