from typing import  List, Optional
from sqlmodel import Field,Relationship,SQLModel
from pydantic import field_validator

class AutorLibroLink(SQLModel, table=True):
    autor_id: Optional[int]=Field(foreign_key="autor.id", primary_key=True)
    libro_id: Optional[int]=Field(foreign_key="libro.id", primary_key=True)

class AutorBase(SQLModel):
    nombre: str | None=Field(default=None, min_length=1, max_length=100, description="Nombre del autor")
    pais_origen: str| None=Field(default=None, min_length=1, max_length=100, description="País de origen del autor" )
    año_nacimiento: int | None=Field(default=0, ge=1800, le=2025, description="Año de nacimiento del autor")

    @field_validator("año_nacimiento")
    def validar_año(cls, v):
        if v and (v < 1800 or v > 2025):
            raise ValueError("El año de nacimiento debe estar entre 1800 y 2025")
        return v
    

class Autor(AutorBase, table=True):
  id: int | None=Field(default=None, primary_key=True)
  active: bool = True
  libros: List["Libro"]=Relationship(back_populates="autores", link_model=AutorLibroLink)


class LibroBase(SQLModel):
    titulo: str | None=Field(default=None, min_length=1, max_length=200, description="Título del libro")
    ISBN: int | None=Field(default=None, ge=1000000000000, le=9999999999999, description="Número ISBN del libro")
    año_publicacion: int | None=Field(default=None, ge=1800, le=2025, description="Año de publicación del libro")
    numero_copias: int | None=Field(default=None, ge=1, description="Número de copias disponibles del libro")

    @field_validator("año_publicacion")
    def validar_año_publicacion(cls, v):
        if v and (v < 1800 or v > 2025):
            raise ValueError("El año de publicación debe estar entre 1800 y 2025")
        return v
    
    @field_validator("ISBN")
    def validar_ISBN(cls, v):
        if v and (v < 1000000000000 or v > 9999999999999):
            raise ValueError("El número ISBN debe tener 13 dígitos")
        return v
       
    

class Libro(LibroBase, table=True):
  id: int | None=Field(default=None, primary_key=True)
  active: bool=True
  autores:List["Autor"]=Relationship(back_populates="libros", link_model=AutorLibroLink)

class LibroAutor(LibroBase):
    autor_id: int=Field(description="ID del autor del libro")