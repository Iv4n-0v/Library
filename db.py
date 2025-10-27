from typing import Annotated, Generator
from fastapi import Depends, FastAPI 
from sqlmodel import Session, SQLModel, create_engine

db_nombre="sqlite:///biblioteca.db"
db_url= f"sqlite:///{db_nombre}"
engine = create_engine(db_nombre, echo=True)

def create_tables(app: FastAPI):
    SQLModel.metadata.create_all(engine)

def get_session()->Generator[Session,None,None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]