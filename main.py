from fastapi import FastAPI
from db import create_tables
import autores, libros

app= FastAPI( title="Libreria Vanegas")
create_tables(app)

app.include_router(autores.router, prefix="/autores")
app.include_router(libros.router, prefix="/libros")
 