from fastapi import APIRouter, HTTPException
from sqlmodel import select,delete
from db import SessionDep
from models import Libro, LibroBase, Autor, AutorLibroLink, LibroAutor

router= APIRouter(tags=["Libros"])

@router.post("/", response_model=Libro)
async def create_libro(libro: LibroBase, session: SessionDep):
    nuevo_libro=Libro.model_validate(libro)
    if not nuevo_libro:
        raise HTTPException(status_code=400, detail="No se pudo crear el libro")
    libro_existente=session.exec(select(Libro).where(Libro.ISBN==libro.ISBN)).first()
    if libro_existente:
        raise HTTPException(status_code=400, detail="Ya existe un libro con este ISBN")
    nuevo_libro.active=True
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
    return {"message":f"Se asignó el Autor con ID {autor_id} al Libro ID {libro_id}"}

@router.get("/todos", response_model=list[Libro])
async def get_libros(session:SessionDep):
   return session.query(Libro).all()

@router.get("/{libro_id}", summary="Obtener libro por ID y sus autores")
async def get_libro(libro_id:int,session:SessionDep):
    libro = session.exec(select(Libro).where(Libro.id == libro_id)).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    autores=session.exec(select(Autor).join(AutorLibroLink).where(AutorLibroLink.libro_id==libro_id)).all()
    return {
        "libro":{"titulo": libro.titulo, "ISBN":libro.ISBN, "Año de publicación":libro.año_publicacion, "Numero de cópias":libro.numero_copias},
        "autores":[{"nombre":autor.nombre, "pais_origen":autor.pais_origen, "año_nacimiento":autor.año_nacimiento} for autor in autores]
    }


@router.post("/LibroAutor", response_model=LibroAutor,summary="Crear Libro con Autor")
async def crear_libro_autor(Libro_Autor:LibroAutor, session:SessionDep):
    nuevo_libro=Libro(titulo=Libro_Autor.titulo, ISBN=Libro_Autor.ISBN, año_publicacion=Libro_Autor.año_publicacion, numero_copias=Libro_Autor.numero_copias, active=True)  
    if not nuevo_libro:
        raise HTTPException(status_code=400, detail="No se pudo crear el libro")
    libro_existente=session.exec(select(Libro).where(Libro.ISBN==Libro_Autor.ISBN)).first()
    if not libro_existente:
        raise HTTPException(status_code=400, detail="Ya existe un libro con este ISBN")
    autor=session.get(Autor,Libro_Autor.autor_id)
    if not autor:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    session.add(nuevo_libro)
    session.commit()
    session.refresh(nuevo_libro)
    link=AutorLibroLink(autor_id=Libro_Autor.autor_id, libro_id=nuevo_libro.id)
    session.add(link)
    session.commit()
    return Libro_Autor

@router.get("/año/{año_publicación}", summary="Obtener el libro por el año de publicación")
async def get_libro_año(año_publicacion: str,session:SessionDep):
    libros=session.exec(select(Libro).where(Libro.año_publicacion==año_publicacion)).all()
    if not libros:
        raise HTTPException(status_code=404,detail="No se encontraron libros en este año")
    return{
        "Libros en el año {año_publicacion}":[{"titulo":libro.titulo, "ISBN":libro.ISBN, "numero_copias":libro.numero_copias} for libro in libros]
    }

@router.patch("/actualizar/{libro_id}", response_model=Libro, summary="Actualizar información del libro")
async def actualizar_libro(libro_id:int,libro_actualizar:LibroBase, session:SessionDep):
    libro=session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404,detail="No se encontró el libro")
    libro_existente=session.exec(select(Libro).where(Libro.ISBN==libro_actualizar.ISBN, Libro.id!=libro_id)).first()
    if libro_existente:
        raise HTTPException(status_code=400, detail="Ya existe un libro con este ISBN o con el mismo ID")
    libro.titulo=libro_actualizar.titulo
    libro.ISBN=libro_actualizar.ISBN
    libro.año_publicacion=libro_actualizar.año_publicacion
    libro.numero_copias=libro_actualizar.numero_copias
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro

@router.delete("/eliminar/{libro_id}", summary="Eliminar un libor por su ID")
async def delete_libro(libro_id:int,session:SessionDep):
    libro=session.get(Libro,libro_id)
    if not libro:
        raise HTTPException(status_code=404,detail="No se encontró el libro")
    if libro.numero_copias<=0:
        raise HTTPException(status_code=400, detail="No se puede eliminar el libro debido a que no tiene copias restantes")
    libro.numero_copias-=1
    if libro.numero_copias==0:
     libro.active=False
    session.exec(delete(AutorLibroLink).where(AutorLibroLink.libro_id==libro_id))
    session.add(libro)
    session.commit()
    return {"message": f"Una copia del libro con ID {libro_id} ha sido eliminado correctamente"}
