import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Float, create_engine, Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# Leer las variables de entorno
DATABASE = os.getenv("DATABASE")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = int(os.getenv("DB_PORT"))

# Crear la URL de conexión a la base de datos
DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"

# Configurar SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

# Definir modelos de base de datos
class Rol(Base):
    __tablename__ = "ROLES"

    id_roles = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rol = Column(Enum('estudiante', 'profesor', 'administrador'), nullable=False)
    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "USUARIOS"

    id_usuarios = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_roles = Column(Integer, ForeignKey("ROLES.id_roles"), nullable=False)
    usuario = Column(String(20), nullable=False, unique=True)
    email = Column(String(150), nullable=False, unique=True)
    contrasena = Column(String(255), nullable=False)
    estado = Column(Enum('activa', 'desactivada'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    perfil = relationship("PerfilUsuario", back_populates="usuario", uselist=False)
    rol = relationship("Rol", back_populates="usuarios")


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


# Tablas adicionales
class Temario(Base):
    __tablename__ = "TEMARIOS"

    id_temario = Column(Integer, primary_key=True, autoincrement=True)
    id_clases = Column(Integer, ForeignKey("CLASES.id_clases"), nullable=False)
    nombre_temario = Column(String(80), nullable=False)
    descrip_temario = Column(String(500), nullable=False)
    contenido = Column(String(100))
    foto_temario = Column(String(100))
    videos_temario = Column(String(100))

class TemarioCuestionario(Base):
    __tablename__ = "TEMARIOS_CUESTIONARIOS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_clases = Column(Integer, ForeignKey("CLASES.id_clases"), nullable=False)
    id_questionario = Column(Integer, ForeignKey("CUESTIONARIOS.id_questionario"), nullable=False)
    id_temario = Column(Integer, ForeignKey("TEMARIOS.id_temario"), nullable=False)

class Clase(Base):
    __tablename__ = "CLASES"

    id_clases = Column(Integer, primary_key=True, autoincrement=True)
    nombre_clases = Column(String(60), nullable=False)
    descripcion_clases = Column(String(500), nullable=False)
    contenido = Column(String(100))
    foto_clases = Column(String(100))
    video_clases = Column(String(100))


class ClaseUsuario(Base):
    __tablename__ = "CLASES_USUARIOS"

    id_usuarios = Column(Integer, ForeignKey("USUARIOS.id_usuarios"), primary_key=True)
    id_clases = Column(Integer, ForeignKey("CLASES.id_clases"), primary_key=True)


class Cuestionario(Base):
    __tablename__ = "CUESTIONARIOS"

    id_questionario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_cuestionario = Column(String(80), nullable=False)
    descrip_cuestionario = Column(String(500), nullable=False)
    foto_cuestionario = Column(String(100))
    video_cuestionario = Column(String(100))


class ResultadoCuestionario(Base):
    __tablename__ = "RESULTADOS_CUESTIONARIOS"

    id_resultado_cuestionario = Column(Integer, primary_key=True, autoincrement=True)
    id_questionario = Column(Integer, ForeignKey("CUESTIONARIOS.id_questionario"), nullable=False)
    id_usuarios = Column(Integer, ForeignKey("USUARIOS.id_usuarios"), nullable=False)
    nota = Column(Integer, nullable=False)
    fecha_completado = Column(DateTime, nullable=False)
    total_correctas = Column(Integer, nullable=False)
    total_falladas = Column(Integer, nullable=False)


class Experimento(Base):
    __tablename__ = "EXPERIMENTOS"

    id_experimento = Column(Integer, primary_key=True, autoincrement=True)
    nombre_experimento = Column(String(80), nullable=False)
    descrip_experimento = Column(String(500), nullable=False)
    foto_experimento = Column(String(100))
    video_experimento = Column(String(100))

class Pregunta(Base):
    __tablename__ = "PREGUNTAS"

    id_pregunta = Column(Integer, primary_key=True, autoincrement=True)
    id_questionario = Column(Integer, ForeignKey("CUESTIONARIOS.id_questionario"), nullable=False)
    enunciado = Column(String(500), nullable=False)
    respuesta = Column(String(500), nullable=False)
    correcta = Column(String(500), nullable=False)
    respuesta1 = Column(String(500), nullable=False)
    respuesta2 = Column(String(500), nullable=False)
    respuesta3 = Column(String(500), nullable=False)


class VideoExperimento(Base):
    __tablename__ = "VIDEOS_EXPERIMENTOS"

    id_video_experimento = Column(Integer, primary_key=True, autoincrement=True)
    id_experimento = Column(Integer, ForeignKey("EXPERIMENTOS.id_experimento"), nullable=False)
    nombre_experimento = Column(String(80), nullable=False)
    descrip_experimento = Column(String(500), nullable=False)
    video_experimento = Column(String(100), nullable=False)


class TemarioExperimento(Base):
    __tablename__ = "TEMARIOS_EXPERIMENTOS"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_temario = Column(Integer, ForeignKey("TEMARIOS.id_temario"), nullable=False)
    id_experimento = Column(Integer, ForeignKey("EXPERIMENTOS.id_experimento"), nullable=False)


class DatoExperimento(Base):
    __tablename__ = "DATOS_EXPERIMENTOS"

    id_datos = Column(String(50), primary_key=True)
    id_experimento = Column(Integer, ForeignKey("EXPERIMENTOS.id_experimento"), nullable=False)
    masa1 = Column(Float)
    masa2 = Column(Float)
    masa3 = Column(Float)
    masa4 = Column(Float)
    velocidad1 = Column(Float)
    velocidad2 = Column(Float)
    velocidad3 = Column(Float)
    velocidad4 = Column(Float)
    velocidad5 = Column(Float)
    altura1 = Column(Float)
    altura2 = Column(Float)
    altura3 = Column(Float)
    altura4 = Column(Float)
    tiempo1 = Column(Float)
    tiempo2 = Column(Float)
    tiempo3 = Column(Float)
    tiempo4 = Column(Float)

# Modelos Pydantic para las respuestas
class RolBase(BaseModel):
    id_roles: int
    rol: str

    class Config:
        orm_mode = True


class UsuarioBase(BaseModel):
    id_usuarios: int
    id_roles: int
    usuario: str
    email: str
    estado: str
    fecha_creacion: datetime
    rol: RolBase

    class Config:
        orm_mode = True


class PerfilUsuarioBase(BaseModel):
    id_usuarios: int
    nombre_completo: str
    genero: str
    pais: Optional[str]
    idioma: Optional[str]
    edad: Optional[int]
    foto_perfil_usuario: Optional[str]

    class Config:
        orm_mode = True


@app.post("/roles/", response_model=RolBase,  tags=["Roles"])
def create_rol(rol: str, db: Session = Depends(get_db)):
    new_rol = Rol(rol=rol)
    db.add(new_rol)
    db.commit()
    db.refresh(new_rol)
    return new_rol


@app.get("/roles/", response_model=List[RolBase],  tags=["Roles"])
def read_roles(db: Session = Depends(get_db)):
    roles = db.query(Rol).all()
    return roles


@app.post("/usuarios/", response_model=UsuarioBase,  tags=["Usuarios"])
def create_usuario(id_roles: int, usuario: str, email: str, contrasena: str, estado: str, db: Session = Depends(get_db)):
    rol = db.query(Rol).filter(Rol.id_roles == id_roles).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    new_usuario = Usuario(
        id_roles=id_roles,
        usuario=usuario,
        email=email,
        contrasena=contrasena,
        estado=estado,
    )
    db.add(new_usuario)
    db.commit()
    db.refresh(new_usuario)
    return new_usuario


@app.post("/usuarios/{id_usuario}/perfil", response_model=PerfilUsuarioBase,  tags=["Usuarios"])
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
    return new_perfil


@app.get("/usuarios/", response_model=List[UsuarioBase],  tags=["Usuarios"])
def read_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios


# Rutas para Clases
@app.post("/clases/", response_model=Clase, tags=["Clases"])
def create_clase(nombre_clases: str, descripcion_clases: str, contenido: str = None, foto_clases: str = None, video_clases: str = None, db: Session = Depends(get_db)):
    nueva_clase = Clase(
        nombre_clases=nombre_clases,
        descripcion_clases=descripcion_clases,
        contenido=contenido,
        foto_clases=foto_clases,
        video_clases=video_clases
    )
    db.add(nueva_clase)
    db.commit()
    db.refresh(nueva_clase)
    return nueva_clase

@app.get("/clases/", response_model=List[Clase], tags=["Clases"])
def read_clases(db: Session = Depends(get_db)):
    clases = db.query(Clase).all()
    return clases

# Rutas para Cuestionarios
@app.post("/cuestionarios/", response_model=Cuestionario, tags=["Cuestionarios"])
def create_cuestionario(nombre_cuestionario: str, descrip_cuestionario: str, foto_cuestionario: str = None, video_cuestionario: str = None, db: Session = Depends(get_db)):
    nuevo_cuestionario = Cuestionario(
        nombre_cuestionario=nombre_cuestionario,
        descrip_cuestionario=descrip_cuestionario,
        foto_cuestionario=foto_cuestionario,
        video_cuestionario=video_cuestionario
    )
    db.add(nuevo_cuestionario)
    db.commit()
    db.refresh(nuevo_cuestionario)
    return nuevo_cuestionario

@app.get("/cuestionarios/", response_model=List[Cuestionario], tags=["Cuestionarios"])
def read_cuestionarios(db: Session = Depends(get_db)):
    cuestionarios = db.query(Cuestionario).all()
    return cuestionarios

# Rutas para Resultados de Cuestionarios
@app.post("/resultados_cuestionarios/", response_model=ResultadoCuestionario, tags=["Resultados Cuestionarios"])
def create_resultado_cuestionario(id_questionario: int, id_usuarios: int, nota: int, fecha_completado: datetime, total_correctas: int, total_falladas: int, db: Session = Depends(get_db)):
    nuevo_resultado = ResultadoCuestionario(
        id_questionario=id_questionario,
        id_usuarios=id_usuarios,
        nota=nota,
        fecha_completado=fecha_completado,
        total_correctas=total_correctas,
        total_falladas=total_falladas
    )
    db.add(nuevo_resultado)
    db.commit()
    db.refresh(nuevo_resultado)
    return nuevo_resultado

@app.get("/resultados_cuestionarios/", response_model=List[ResultadoCuestionario], tags=["Resultados Cuestionarios"])
def read_resultados_cuestionarios(db: Session = Depends(get_db)):
    resultados = db.query(ResultadoCuestionario).all()
    return resultados

# Rutas para Temarios
@app.post("/temarios/", response_model=Temario, tags=["Temarios"])
def create_temario(id_clases: int, nombre_temario: str, descrip_temario: str, contenido: str = None, foto_temario: str = None, videos_temario: str = None, db: Session = Depends(get_db)):
    nuevo_temario = Temario(
        id_clases=id_clases,
        nombre_temario=nombre_temario,
        descrip_temario=descrip_temario,
        contenido=contenido,
        foto_temario=foto_temario,
        videos_temario=videos_temario
    )
    db.add(nuevo_temario)
    db.commit()
    db.refresh(nuevo_temario)
    return nuevo_temario

@app.get("/temarios/", response_model=List[Temario], tags=["Temarios"])
def read_temarios(db: Session = Depends(get_db)):
    temarios = db.query(Temario).all()
    return temarios

# Rutas para Experimentos
@app.post("/experimentos/", response_model=Experimento, tags=["Experimentos"])
def create_experimento(nombre_experimento: str, descrip_experimento: str, foto_experimento: str = None, video_experimento: str = None, db: Session = Depends(get_db)):
    nuevo_experimento = Experimento(
        nombre_experimento=nombre_experimento,
        descrip_experimento=descrip_experimento,
        foto_experimento=foto_experimento,
        video_experimento=video_experimento
    )
    db.add(nuevo_experimento)
    db.commit()
    db.refresh(nuevo_experimento)
    return nuevo_experimento

@app.get("/experimentos/", response_model=List[Experimento], tags=["Experimentos"])
def read_experimentos(db: Session = Depends(get_db)):
    experimentos = db.query(Experimento).all()
    return experimentos

# Rutas para Preguntas
@app.post("/preguntas/", response_model=Pregunta, tags=["Preguntas"])
def create_pregunta(id_questionario: int, enunciado: str, respuesta: str, correcta: str, respuesta1: str, respuesta2: str, respuesta3: str, db: Session = Depends(get_db)):
    nueva_pregunta = Pregunta(
        id_questionario=id_questionario,
        enunciado=enunciado,
        respuesta=respuesta,
        correcta=correcta,
        respuesta1=respuesta1,
        respuesta2=respuesta2,
        respuesta3=respuesta3
    )
    db.add(nueva_pregunta)
    db.commit()
    db.refresh(nueva_pregunta)
    return nueva_pregunta

@app.get("/preguntas/", response_model=List[Pregunta], tags=["Preguntas"])
def read_preguntas(db: Session = Depends(get_db)):
    preguntas = db.query(Pregunta).all()
    return preguntas

# Rutas para Clases Usuarios
@app.post("/clases_usuarios/", response_model=dict, tags=["Clases Usuarios"])
def create_clase_usuario(id_usuarios: int, id_clases: int, db: Session = Depends(get_db)):
    nueva_clase_usuario = ClaseUsuario(
        id_usuarios=id_usuarios,
        id_clases=id_clases
    )
    db.add(nueva_clase_usuario)
    db.commit()
    return {"message": "Usuario asignado a la clase con éxito"}

@app.get("/clases_usuarios/", response_model=List[ClaseUsuario], tags=["Clases Usuarios"])
def read_clases_usuarios(db: Session = Depends(get_db)):
    clases_usuarios = db.query(ClaseUsuario).all()
    return clases_usuarios

# Rutas para Temarios Cuestionarios
@app.post("/temarios_cuestionarios/", response_model=dict, tags=["Temarios Cuestionarios"])
def create_temario_cuestionario(id_clases: int, id_questionario: int, id_temario: int, db: Session = Depends(get_db)):
    nuevo_temario_cuestionario = TemarioCuestionario(
        id_clases=id_clases,
        id_questionario=id_questionario,
        id_temario=id_temario
    )
    db.add(nuevo_temario_cuestionario)
    db.commit()
    return {"message": "Cuestionario asignado al temario con éxito"}

@app.get("/temarios_cuestionarios/", response_model=List[TemarioCuestionario], tags=["Temarios Cuestionarios"])
def read_temarios_cuestionarios(db: Session = Depends(get_db)):
    temarios_cuestionarios = db.query(TemarioCuestionario).all()
    return temarios_cuestionarios

# Rutas para Videos Experimentos
@app.post("/videos_experimentos/", response_model=VideoExperimento, tags=["Videos Experimentos"])
def create_video_experimento(id_experimento: int, nombre_experimento: str, descrip_experimento: str, video_experimento: str, db: Session = Depends(get_db)):
    nuevo_video_experimento = VideoExperimento(
        id_experimento=id_experimento,
        nombre_experimento=nombre_experimento,
        descrip_experimento=descrip_experimento,
        video_experimento=video_experimento
    )
    db.add(nuevo_video_experimento)
    db.commit()
    db.refresh(nuevo_video_experimento)
    return nuevo_video_experimento

@app.get("/videos_experimentos/", response_model=List[VideoExperimento], tags=["Videos Experimentos"])
def read_videos_experimentos(db: Session = Depends(get_db)):
    videos_experimentos = db.query(VideoExperimento).all()
    return videos_experimentos

# Rutas para Datos Experimentos
@app.post("/datos_experimentos/", response_model=DatoExperimento, tags=["Datos Experimentos"])
def create_datos_experimento(id_datos: str, id_experimento: int, masa1: float = None, masa2: float = None, masa3: float = None, masa4: float = None, velocidad1: float = None, velocidad2: float = None, velocidad3: float = None, velocidad4: float = None, velocidad5: float = None, altura1: float = None, altura2: float = None, altura3: float = None, altura4: float = None, tiempo1: float = None, tiempo2: float = None, tiempo3: float = None, tiempo4: float = None, db: Session = Depends(get_db)):
    nuevo_dato_experimento = DatoExperimento(
        id_datos=id_datos,
        id_experimento=id_experimento,
        masa1=masa1,
        masa2=masa2,
        masa3=masa3,
        masa4=masa4,
        velocidad1=velocidad1,
        velocidad2=velocidad2,
        velocidad3=velocidad3,
        velocidad4=velocidad4,
        velocidad5=velocidad5,
        altura1=altura1,
        altura2=altura2,
        altura3=altura3,
        altura4=altura4,
        tiempo1=tiempo1,
        tiempo2=tiempo2,
        tiempo3=tiempo3,
        tiempo4=tiempo4
    )
    db.add(nuevo_dato_experimento)
    db.commit()
    db.refresh(nuevo_dato_experimento)
    return nuevo_dato_experimento

@app.get("/datos_experimentos/", response_model=List[DatoExperimento], tags=["Datos Experimentos"])
def read_datos_experimentos(db: Session = Depends(get_db)):
    datos_experimentos = db.query(DatoExperimento).all()
    return datos_experimentos

# Rutas para Temarios Experimentos
@app.post("/temarios_experimentos/", response_model=dict, tags=["Temarios Experimentos"])
def create_temario_experimento(id_temario: int, id_experimento: int, db: Session = Depends(get_db)):
    nuevo_temario_experimento = TemarioExperimento(
        id_temario=id_temario,
        id_experimento=id_experimento
    )
    db.add(nuevo_temario_experimento)
    db.commit()
    return {"message": "Experimento asignado al temario con éxito"}

@app.get("/temarios_experimentos/", response_model=List[TemarioExperimento], tags=["Temarios Experimentos"])
def read_temarios_experimentos(db: Session = Depends(get_db)):
    temarios_experimentos = db.query(TemarioExperimento).all()
    return temarios_experimentos


@app.get("/health/", response_model=dict, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
