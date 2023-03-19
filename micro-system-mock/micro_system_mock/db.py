from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from .config import settings


db_url = settings.DB_CONNECTION_STRING
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    message = Column(String)

    def to_pydantic(self):
        return {"id": self.id, "log": self.log}


class LogCreate(BaseModel):
    message: str


def get_logs():
    session = Session()
    logs = session.query(Log).all()
    session.close()
    return [u.to_pydantic() for u in logs]


def create_log(log: LogCreate):
    session = Session()
    user_obj = Log(name=log.message)
    session.add(user_obj)
    session.commit()
    session.close()
