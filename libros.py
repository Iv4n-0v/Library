from fastapi import APIRouter, HTTPException
from sqlmodel import select
from db import SessionDep
from models import Libro, LibroBase, Autor, AutorLibroLink

router= APIRouter(tags=["Libros"])

@router.post("/", response_model=Libro)
async def create_libro(libro: LibroBase, session: SessionDep):
    nuevo_libro=Libro.model_validate(libro)
    if not nuevo_libro:
        raise HTTPException(status_code=400, detail="No se pudo crear el libro")
    session.add(nuevo_libro)
    session.commit()
    session.refresh(nuevo_libro)
    return nuevo_libro

@router.post("/aignar_autor/{libro_id}/{autor_id}", response_model=Libro)
async def asignar_autor_libro(libro_id:int,autor_id:int,session:SessionDep):
    libro=session.get(Libro,libro_id)
    autor=session.get(Autor,autor_id)
    if not libro or not autor:
        raise HTTPException(status_code=404, detail="Libro o Autor no encontrado")
    link=AutorLibroLink(autor_id=autor_id, libro_id=libro_id)
    session.add(link)
    session.commit()
    return {"message":f"Se asignó el Autor ID {autor_id} al Libro ID {libro_id}"}

@router.get("/todos", response_model=list[Libro])
async def get_libros(session:SessionDep):
   return session.query(Libro).all()

@router.get("/{libro_id}", response_model=Libro)
async def get_libro(libro_id:int,session:SessionDep):
    libro = session.get(Libro,libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro
