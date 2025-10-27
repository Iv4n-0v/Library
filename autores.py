from fastapi import APIRouter, HTTPException
from sqlmodel import select
from db import SessionDep
from models import Autor, AutorBase, Libro

router = APIRouter(tags=["Autores"])


@router.post("/", response_model=Autor)
async def create_autor(autor: AutorBase, session: SessionDep):
    nuevo_autor=Autor.model_validate(autor)
    if not nuevo_autor:
        raise HTTPException(status_code=400, detail="No se pudo crear el autor")
    session.add(nuevo_autor)
    session.commit()
    session.refresh(nuevo_autor)
    
    return nuevo_autor

@router.get("/todos", response_model=list[Autor])
async def get_autores(session: SessionDep):
    return session.query(Autor).all()   