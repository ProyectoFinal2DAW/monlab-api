import os
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Enum, Timestamp, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship

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

# Definir modelos
class Usuario(Base):
    __tablename__ = "USUARIOS"

    id_usuarios = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_roles = Column(Integer, nullable=False)
    usuario = Column(String(20), nullable=False)
    email = Column(String(150), nullable=False)
    contrasena = Column(String(255), nullable=False)
    estado = Column(Enum('activa', 'desactivada'), nullable=False)
    fecha_creacion = Column(Timestamp, nullable=False)
    perfil = relationship("PerfilUsuario", back_populates="usuario")

class PerfilUsuario(Base):
    __tablename__ = "PERFIL_USUARIOS"

    id_usuarios = Column(Integer, ForeignKey("USUARIOS.id_usuarios"), primary_key=True)
    nombre_completo = Column(String(100), nullable=False)
    genero = Column(Enum('hombre', 'mujer', 'no binario', 'prefiero no decirlo'), nullable=False)
    pais = Column(String(60))
    idioma = Column(Enum('catalan', 'castellano', 'ingles'))
    edad = Column(Integer, nullable=False)
    foto_perfil_usuario = Column(String(100))
    usuario = relationship("Usuario", back_populates="perfil")

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

# Endpoint para agregar un usuario
@app.post("/usuarios/", response_model=dict)
def create_usuario(id_roles: int, usuario: str, email: str, contrasena: str, estado: str, db: Session = Depends(get_db)):
    new_usuario = Usuario(
        id_roles=id_roles,
        usuario=usuario,
        email=email,
        contrasena=contrasena,
        estado=estado,
        fecha_creacion="CURRENT_TIMESTAMP"
    )
    db.add(new_usuario)
    db.commit()
    db.refresh(new_usuario)
    return {"id_usuarios": new_usuario.id_usuarios, "usuario": new_usuario.usuario}

# Endpoint para agregar un perfil de usuario
@app.post("/usuarios/{id_usuario}/perfil", response_model=dict)
def create_perfil(id_usuario: int, nombre_completo: str, genero: str, pais: str = None, idioma: str = None, edad: int = None, foto_perfil_usuario: str = None, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuarios == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    new_perfil = PerfilUsuario(
        id_usuarios=id_usuario,
        nombre_completo=nombre_completo,
        genero=genero,
        pais=pais,
        idioma=idioma,
        edad=edad,
        foto_perfil_usuario=foto_perfil_usuario
    )
    db.add(new_perfil)
    db.commit()
    db.refresh(new_perfil)
    return {"id_usuarios": new_perfil.id_usuarios, "nombre_completo": new_perfil.nombre_completo}

# Endpoint para listar usuarios
@app.get("/usuarios/", response_model=list)
def read_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios

# Endpoint para manejar errores de conexión
@app.get("/health/", response_model=dict)
def health_check(db: Session = Depends(get_db)):
    try:
        # Intentar una consulta simple
        db.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")