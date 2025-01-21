import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Leer las variables de entorno
DATABASE = os.getenv("DATABASE", "test_db")
USER = os.getenv("DB_USER", "root")
PASSWORD = os.getenv("DB_PASSWORD", "password")
HOST = os.getenv("DB_HOST", "localhost")
PORT = os.getenv("DB_PORT", "3306")

# Crear la URL de conexión a la base de datos
DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# Configurar SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definir un modelo de ejemplo
class ExampleModel(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Crear la instancia de FastAPI
app = FastAPI()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para agregar un registro de ejemplo
@app.post("/examples/", response_model=dict)
def create_example(name: str, db: Session = Depends(get_db)):
    new_example = ExampleModel(name=name)
    db.add(new_example)
    db.commit()
    db.refresh(new_example)
    return {"id": new_example.id, "name": new_example.name}

# Endpoint para listar registros de ejemplo
@app.get("/examples/", response_model=list)
def read_examples(db: Session = Depends(get_db)):
    examples = db.query(ExampleModel).all()
    return examples

# Endpoint para manejar errores de conexión
@app.get("/health/", response_model=dict)
def health_check(db: Session = Depends(get_db)):
    try:
        # Intentar una consulta simple
        db.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")