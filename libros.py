from fastapi import APIRouter, HTTPException
from sqlmodel import select
from db import SessionDep
from models import Libro, LibroBase

router= APIRouter(tags=["Libros"])

@router.post("/libros", response_model=Libro)
async def create_libro(libro: LibroBase, session: SessionDep):
    nuevo_libro=Libro.model_validate(libro)
    if not nuevo_libro:
        raise HTTPException(status_code=400, detail="No se pudo crear el libro")
    session.add(nuevo_libro)
    session.commit()
    session.refresh(nuevo_libro)
    return nuevo_libro