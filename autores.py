from fastapi import APIRouter, HTTPException
from sqlmodel import select, delete
from db import SessionDep
from models import Autor, AutorBase, Libro, AutorLibroLink

router = APIRouter(tags=["Autores"])


@router.post("/", response_model=Autor)
async def create_autor(autor: AutorBase, session: SessionDep):
    nuevo_autor=Autor.model_validate(autor)
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
    relacion_existente=session.exec(select(AutorLibroLink).where((AutorLibroLink.autor_id==autor_id) & (AutorLibroLink.libro_id==libro_id))).first()
    if relacion_existente:
        raise HTTPException(status_code=409, detail="El libro ya está asignado a este autor")
    link=AutorLibroLink(autor_id=autor_id, libro_id=libro_id)
    session.add(link)
    session.commit()
    return {"message":f"Se asignó el Libro al Autor"}

@router.get("/todos", response_model=list[Autor])
async def get_autores(session: SessionDep):
    return session.query(Autor).all() 

@router.get("/libros/{autor_id}", summary="Obtener autor por ID y sus libros")
async def get_autores(autor_id:int,session:SessionDep):
    autor=session.exec(select(Autor).where(Autor.id==autor_id)).first()
    if not autor:
     raise HTTPException(status_code=404, detail="Autor no encontrado")
    libros=session.exec(select(Libro).join(AutorLibroLink).where(AutorLibroLink.autor_id==autor_id)).all()
    return {
       "autor": {"nombre": autor.nombre, "pais_origen": autor.pais_origen, "año_nacimiento": autor.año_nacimiento},
       "libros":[{"nombre": libro.titulo, "ISBN": libro.ISBN, "año_publicacion": libro.año_publicacion, "numero_copias": libro.numero_copias}for libro in libros],
    }

@router.get("/pais/{pais_origen}", summary="Obtener autores por país de origen")
async def get_autores_por_pais(pais_origen:str, session:SessionDep):
    autores=session.exec(select(Autor).where(Autor.pais_origen==pais_origen)).all()
    if not autores:
        raise HTTPException(status_code=404, detail="No se encontraron autores de este país")
    return{
         "pais_origen": pais_origen,
         "autores":[{"nombre": autor.nombre, "año_nacimiento": autor.año_nacimiento} for autor in autores]
    }

@router.patch("/actualizar/{autor_id}", response_model=Autor, summary="Actualizar información del autor")
async def patch_autor(autor_id:int,autor_actualizar:AutorBase,session:SessionDep):
    autor=session.get(Autor, autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    autor.nombre=autor_actualizar.nombre
    autor.pais_origen=autor_actualizar.pais_origen
    autor.año_nacimiento=autor_actualizar.año_nacimiento
    session.add(autor)
    session.commit()
    session.refresh(autor)
    return autor

@router.delete("/eliminar/{autor_id}", summary="Eliminar autor por su ID")
async def delete_autor(autor_id:int,session:SessionDep):
   autor=session.get(Autor, autor_id)
   if not autor:
      raise HTTPException(status_code=404,detail="No se encontró el autor")
   autor.active=False
   session.exec(delete(AutorLibroLink).where(AutorLibroLink.autor_id==autor_id))
   session.add(autor)
   session.commit()
   return {"message":f"El autor con ID {autor_id} ha sido eliminado correctamente"}