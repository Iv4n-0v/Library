from typing import  List, Optional
from sqlmodel import Field,Relationship,SQLModel

class AutorLibroLink(SQLModel, table=True):
    autor_id: Optional[int]=Field(foreign_key="autor.id", primary_key=True)
    libro_id: Optional[int]=Field(foreign_key="libro.id", primary_key=True)

class AutorBase(SQLModel):
    nombre: str | None
    pais_origen: str| None
    año_nacimiento: int | None

class Autor(AutorBase, table=True):
  id: int | None=Field(default=None, primary_key=True)
  active: bool = True
  libros: List["Libro"]=Relationship(back_populates="autores", link_model=AutorLibroLink)


class LibroBase(SQLModel):
    titulo: str | None
    ISBN: int | None
    año_publicacion: int | None
    numero_copias: int | None

class Libro(LibroBase, table=True):
  id: int | None=Field(default=None, primary_key=True)
  
  autores:List["Autor"]=Relationship(back_populates="libros", link_model=AutorLibroLink)
