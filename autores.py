from fastapi import APIRouter, HTTPException
from sqlmodel import select
from db import SessionDep
from models import Autor, AutorBase, Libro, AutorLibroLink

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

@router.post("/asignar_libro/{autor_id}/{libro_id}", response_model=Autor, summary="Asignar libro a autor")
async def asignar_libro_autor(autor_id:int,libro_id:int,session:SessionDep):
    autor=session.get(Autor, autor_id)
    libro=session.get(Libro,libro_id)
    if not autor or not libro:
     raise HTTPException(status_code=404, detail="Autor o Libro no encontrado")
    link=AutorLibroLink(autor_id=autor_id, libro_id=libro_id)
    session.add(link)
    session.commit()
    return {"message":f"Se asignó el Libro ID {libro_id} al Autor ID {autor_id}"}

@router.get("/todos", response_model=list[Autor])
async def get_autores(session: SessionDep):
    return session.query(Autor).all() 

@router.get("/{autor_id}", summary="Obtener autor por ID")
async def get_autores(autor_id:int,session:SessionDep):
    autor=session.exec(select(Autor).where(Autor.id==autor_id)).first()
    if not autor:
     raise HTTPException(status_code=404, detail="Autor no encontrado")
    libros=session.exec(select(Libro).join(AutorLibroLink).where(AutorLibroLink.autor_id==autor_id)).all()
    return {
       "autor": {"nombre": autor.nombre, "pais_origen": autor.pais_origen, "año_nacimiento": autor.año_nacimiento},
       "libros":[{"nombre": libro.titulo, "ISBN": libro.ISBN, "año_publicacion": libro.año_publicacion, "numero_copias": libro.numero_copias}for libro in libros],
    }

  

