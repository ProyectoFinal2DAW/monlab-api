import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Float, create_engine, Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

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


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from this origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


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
    rol = Column(String(20), nullable=False, unique=True)
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

# Agrega la definición de la tabla Videos, si aún no existe
class Video(Base):
    __tablename__ = "VIDEOS"
    
    idVideo = Column(Integer, primary_key=True, autoincrement=True)
    imagenVideo = Column(String(100))
    rutaVideo = Column(String(200))
    tituloVideo = Column(String(100))
    idClase = Column(Integer, ForeignKey("CLASES.id_clases"), nullable=False)


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
    __tablename__ = "TEMEARIOS_CUESTIONARIOS"

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
    fecha_publicacion = Column(DateTime, default=datetime.utcnow)


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




class ClaseDetail(BaseModel):
    id_clases: int
    nombre_clases: str
    descripcion_clases: str
    foto_clases: Optional[str] = None

    class Config:
        orm_mode = True


class ResultadoAlumnoResponse(BaseModel):
    id_resultado_cuestionario: int
    id_questionario: int
    id_usuarios: int
    nota: int
    fecha_completado: datetime
    total_correctas: int
    total_falladas: int

    class Config:
        orm_mode = True

class TemarioDetail(BaseModel):
    id_temario: int
    id_clases: int
    nombre_temario: str
    descrip_temario: str
    contenido: Optional[str] = None
    foto_temario: Optional[str] = None
    videos_temario: Optional[str] = None

    class Config:
        orm_mode = True

class CuestionarioResponse(BaseModel):
    id_questionario: int
    nombre_cuestionario: str
    fecha_publicacion: datetime

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




class ExperimentoDetail(BaseModel):
    id_experimento: int
    nombre_experimento: str
    descrip_experimento: str
    foto_experimento: Optional[str]
    video_experimento: Optional[str]

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

class CuestionarioDetail(BaseModel):
    id_questionario: int
    nombre_cuestionario: str
    descrip_cuestionario: str
    foto_cuestionario: Optional[str] = None
    video_cuestionario: Optional[str] = None
    fecha_publicacion: datetime

    class Config:
        orm_mode = True

#Rutas roles
@app.post("/roles/", response_model=RolBase, tags=["Roles"])
def create_rol(rol: str, db: Session = Depends(get_db)):
    new_rol = Rol(rol=rol)
    db.add(new_rol)
    db.commit()
    db.refresh(new_rol)
    return new_rol


@app.get("/roles/", response_model=List[RolBase], tags=["Roles"])
def read_roles(db: Session = Depends(get_db)):
    roles = db.query(Rol).all()
    return roles


@app.get("/temarios/contenido/{id_clases}", response_model=List[str], tags=["Temarios"])
def get_contenido_temarios_by_clase(id_clases: int, db: Session = Depends(get_db)):
    # Se consulta únicamente el campo "contenido" de aquellos temarios con el id_clases especificado
    temarios = db.query(Temario.contenido).filter(Temario.id_clases == id_clases).all()
    if not temarios:
        raise HTTPException(status_code=404, detail="No se encontraron temarios para la clase especificada")
    # Cada resultado se devuelve como una tupla, se extrae el primer elemento (contenido)
    return [contenido for (contenido,) in temarios if contenido is not None]

@app.get("/temarios/clase/{id_clases}", response_model=List[TemarioDetail], tags=["Temarios"])
def get_temarios_by_clase(id_clases: int, db: Session = Depends(get_db)):
    temarios = db.query(Temario).filter(Temario.id_clases == id_clases).all()
    if not temarios:
        raise HTTPException(status_code=404, detail="No se encontraron temarios para la clase especificada")
    return temarios

@app.get("/temarios/clase/{id_clases}/videos", tags=["Temarios"])
def get_videos_temarios_by_clase(id_clases: int, db: Session = Depends(get_db)):
    videos = db.query(Temario.videos_temario).filter(Temario.id_clases == id_clases).all()
    if not videos:
        raise HTTPException(status_code=404, detail="No se encontraron temarios para la clase especificada")
    videos_list = [video for (video,) in videos if video is not None]
    if not videos_list:
        raise HTTPException(status_code=404, detail="No se encontraron videos disponibles para la clase especificada")
    return videos_list

@app.delete("/roles/{role_id}", response_model=RolBase, tags=["Roles"])
def delete_rol(role_id: int, db: Session = Depends(get_db)):
    rol = db.query(Rol).filter(Rol.id_roles == role_id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    db.delete(rol)
    db.commit()
    return rol


@app.get("/clases/{clase_id}", response_model=ClaseDetail, tags=["Clases"])
def get_clase(clase_id: int, db: Session = Depends(get_db)):
    clase = db.query(Clase).filter(Clase.id_clases == clase_id).first()
    if not clase:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    return clase


@app.put("/roles/{role_id}", response_model=RolBase, tags=["Roles"])
def update_rol(role_id: int, rol: str, db: Session = Depends(get_db)):
    existing_rol = db.query(Rol).filter(Rol.id_roles == role_id).first()
    if not existing_rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    existing_rol.rol = rol
    db.commit()
    db.refresh(existing_rol)
    return existing_rol

@app.get("/experimentos/{experimento_id}", response_model=ExperimentoDetail, tags=["Experimentos"])
def get_experimento(experimento_id: int, db: Session = Depends(get_db)):
    experimento = db.query(Experimento).filter(Experimento.id_experimento == experimento_id).first()
    if not experimento:
        raise HTTPException(status_code=404, detail="Experimento no encontrado")
    return experimento



#Rutas usuarios
@app.post("/usuarios/", response_model=UsuarioBase, tags=["Usuarios"])
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


@app.get("/usuarios/", response_model=List[UsuarioBase], tags=["Usuarios"])
def read_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios


@app.delete("/usuarios/{id_usuario}", response_model=UsuarioBase, tags=["Usuarios"])
def delete_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.id_usuarios == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return usuario


@app.put("/usuarios/{id_usuario}", response_model=UsuarioBase, tags=["Usuarios"])
def update_usuario(id_usuario: int, id_roles: int, usuario: str, email: str, contrasena: str, estado: str, db: Session = Depends(get_db)):
    existing_usuario = db.query(Usuario).filter(Usuario.id_usuarios == id_usuario).first()
    if not existing_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    existing_usuario.id_roles = id_roles
    existing_usuario.usuario = usuario
    existing_usuario.email = email
    existing_usuario.contrasena = contrasena
    existing_usuario.estado = estado
    db.commit()
    db.refresh(existing_usuario)
    return existing_usuario


@app.get("/clases/{clase_id}", response_model=ClaseDetail, tags=["Clases"])
def get_clase(clase_id: int, db: Session = Depends(get_db)):
    clase = db.query(Clase).filter(Clase.id_clases == clase_id).first()
    if not clase:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    return clase

#Rutas perfil usuarios

@app.post("/usuarios/{id_usuario}/perfil", response_model=PerfilUsuarioBase, tags=["Perfil Usuarios"])
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

# Endpoint GET para obtener los cuestionarios dependiendo del id_clases
@app.get("/cuestionarios/clase/{id_clases}", response_model=List[CuestionarioResponse], tags=["Cuestionarios"])
def get_cuestionarios_por_clase(id_clases: int, db: Session = Depends(get_db)):
    cuestionarios = (
        db.query(
            Cuestionario.id_questionario,
            Cuestionario.nombre_cuestionario,
            Cuestionario.fecha_publicacion
        )
        .join(TemarioCuestionario, Cuestionario.id_questionario == TemarioCuestionario.id_questionario)
        .filter(TemarioCuestionario.id_clases == id_clases)
        .all()
    )
    if not cuestionarios:
        raise HTTPException(status_code=404, detail="No se encontraron cuestionarios para la clase especificada")
    return cuestionarios


#Rutas clases

@app.post("/clases/", tags=["Clases"])
def create_clase(nombre_clases: str, descripcion_clases: str, contenido: str = None, foto_clases: str = None, video_clases: str = None, db: Session = Depends(get_db)):
    new_clase = Clase(
        nombre_clases=nombre_clases,
        descripcion_clases=descripcion_clases,
        contenido=contenido,
        foto_clases=foto_clases,
        video_clases=video_clases
    )
    db.add(new_clase)
    db.commit()
    db.refresh(new_clase)
    return new_clase


@app.get("/clases/", tags=["Clases"])
def read_clases(db: Session = Depends(get_db)):
    clases = db.query(Clase).all()
    return clases


@app.put("/clases/{clase_id}", tags=["Clases"])
def update_clase(clase_id: int, nombre_clases: str, descripcion_clases: str, contenido: str = None, foto_clases: str = None, video_clases: str = None, db: Session = Depends(get_db)):
    existing_clase = db.query(Clase).filter(Clase.id_clases == clase_id).first()
    if not existing_clase:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    existing_clase.nombre_clases = nombre_clases
    existing_clase.descripcion_clases = descripcion_clases
    existing_clase.contenido = contenido
    existing_clase.foto_clases = foto_clases
    existing_clase.video_clases = video_clases
    db.commit()
    db.refresh(existing_clase)
    return existing_clase

@app.delete("/clases/{clase_id}", tags=["Clases"])
def delete_clase(clase_id: int, db: Session = Depends(get_db)):
    clase = db.query(Clase).filter(Clase.id_clases == clase_id).first()
    if not clase:
        raise HTTPException(status_code=404, detail="Clase no encontrada")
    db.delete(clase)
    db.commit()
    return clase

# Rutas para Cuestionarios
@app.post("/cuestionarios/", tags=["Cuestionarios"])
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


@app.get("/cuestionarios/{cuestionario_id}", response_model=CuestionarioDetail, tags=["Cuestionarios"])
def get_cuestionario(cuestionario_id: int, db: Session = Depends(get_db)):
    cuestionario = db.query(Cuestionario).filter(Cuestionario.id_questionario == cuestionario_id).first()
    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    return cuestionario


@app.get("/cuestionarios/", tags=["Cuestionarios"])
def read_cuestionarios(db: Session = Depends(get_db)):
    cuestionarios = db.query(Cuestionario).all()
    return cuestionarios


@app.put("/cuestionarios/{cuestionario_id}", tags=["Cuestionarios"])
def update_cuestionario(cuestionario_id: int, nombre_cuestionario: str, descrip_cuestionario: str, foto_cuestionario: str = None, video_cuestionario: str = None, db: Session = Depends(get_db)):
    existing_cuestionario = db.query(Cuestionario).filter(Cuestionario.id_questionario == cuestionario_id).first()
    if not existing_cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    existing_cuestionario.nombre_cuestionario = nombre_cuestionario
    existing_cuestionario.descrip_cuestionario = descrip_cuestionario
    existing_cuestionario.foto_cuestionario = foto_cuestionario
    existing_cuestionario.video_cuestionario = video_cuestionario
    db.commit()
    db.refresh(existing_cuestionario)
    return existing_cuestionario


@app.delete("/cuestionarios/{cuestionario_id}", tags=["Cuestionarios"])
def delete_cuestionario(cuestionario_id: int, db: Session = Depends(get_db)):
    cuestionario = db.query(Cuestionario).filter(Cuestionario.id_questionario == cuestionario_id).first()
    if not cuestionario:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    db.delete(cuestionario)
    db.commit()
    return cuestionario

# Rutas para Resultados de Cuestionarios
@app.post("/resultados_cuestionarios/", tags=["Resultados cuestionarios"])
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

@app.get("/notas/clase/{id_clases}/usuario/{id_usuario}", response_model=List[ResultadoAlumnoResponse], tags=["Notas"])
def get_notas_por_clase_usuario(id_clases: int, id_usuario: int, db: Session = Depends(get_db)):
    resultados = (
        db.query(ResultadoCuestionario)
        .join(TemarioCuestionario, ResultadoCuestionario.id_questionario == TemarioCuestionario.id_questionario)
        .filter(ResultadoCuestionario.id_usuarios == id_usuario, TemarioCuestionario.id_clases == id_clases)
        .all()
    )
    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron resultados para la clase y el usuario especificados")
    return resultados


@app.get("/resultados_cuestionarios/", tags=["Resultados cuestionarios"])
def read_resultados_cuestionarios(db: Session = Depends(get_db)):
    resultados = db.query(ResultadoCuestionario).all()
    return resultados


@app.put("/resultados_cuestionarios/{resultado_id}", tags=["Resultados cuestionarios"])
def update_resultado_cuestionario(resultado_id: int, id_questionario: int, id_usuarios: int, nota: int, fecha_completado: datetime, total_correctas: int, total_falladas: int, db: Session = Depends(get_db)):
    existing_resultado = db.query(ResultadoCuestionario).filter(ResultadoCuestionario.id_resultado_cuestionario == resultado_id).first()
    if not existing_resultado:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")
    existing_resultado.id_questionario = id_questionario
    existing_resultado.id_usuarios = id_usuarios
    existing_resultado.nota = nota
    existing_resultado.fecha_completado = fecha_completado
    existing_resultado.total_correctas = total_correctas
    existing_resultado.total_falladas = total_falladas
    db.commit()
    db.refresh(existing_resultado)
    return existing_resultado


@app.delete("/resultados_cuestionarios/{resultado_id}", tags=["Resultados cuestionarios"])
def delete_resultado_cuestionario(resultado_id: int, db: Session = Depends(get_db)):
    resultado = db.query(ResultadoCuestionario).filter(ResultadoCuestionario.id_resultado_cuestionario == resultado_id).first()
    if not resultado:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")
    db.delete(resultado)
    db.commit()
    return resultado

# Rutas para Temarios
@app.post("/temarios/", tags=["Temarios"])
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


@app.get("/temarios/", tags=["Temarios"])
def read_temarios(db: Session = Depends(get_db)):
    temarios = db.query(Temario).all()
    return temarios


@app.put("/temarios/{temario_id}", tags=["Temarios"])
def update_temario(temario_id: int, id_clases: int, nombre_temario: str, descrip_temario: str, contenido: str = None, foto_temario: str = None, videos_temario: str = None, db: Session = Depends(get_db)):
    existing_temario = db.query(Temario).filter(Temario.id_temario == temario_id).first()
    if not existing_temario:
        raise HTTPException(status_code=404, detail="Temario no encontrado")
    existing_temario.id_clases = id_clases
    existing_temario.nombre_temario = nombre_temario
    existing_temario.descrip_temario = descrip_temario
    existing_temario.contenido = contenido
    existing_temario.foto_temario = foto_temario
    existing_temario.videos_temario = videos_temario
    db.commit()
    db.refresh(existing_temario)
    return existing_temario


@app.delete("/temarios/{temario_id}", tags=["Temarios"])
def delete_temario(temario_id: int, db: Session = Depends(get_db)):
    temario = db.query(Temario).filter(Temario.id_temario == temario_id).first()
    if not temario:
        raise HTTPException(status_code=404, detail="Temario no encontrado")
    db.delete(temario)
    db.commit()
    return temario


@app.get("/temarios/{temario_id}", response_model=TemarioDetail, tags=["Temarios"])
def get_temario(temario_id: int, db: Session = Depends(get_db)):
    temario = db.query(Temario).filter(Temario.id_temario == temario_id).first()
    if not temario:
        raise HTTPException(status_code=404, detail="Temario no encontrado")
    return temario

# Rutas para Experimentos
@app.post("/experimentos/", tags=["Experimentos"])
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


@app.get("/experimentos/", tags=["Experimentos"])
def read_experimentos(db: Session = Depends(get_db)):
    experimentos = db.query(Experimento).all()
    return experimentos

@app.put("/experimentos/{experimento_id}", tags=["Experimentos"])
def update_experimento(experimento_id: int, nombre_experimento: str, descrip_experimento: str, foto_experimento: str = None, video_experimento: str = None, db: Session = Depends(get_db)):
    existing_experimento = db.query(Experimento).filter(Experimento.id_experimento == experimento_id).first()
    if not existing_experimento:
        raise HTTPException(status_code=404, detail="Experimento no encontrado")
    existing_experimento.nombre_experimento = nombre_experimento
    existing_experimento.descrip_experimento = descrip_experimento
    existing_experimento.foto_experimento = foto_experimento
    existing_experimento.video_experimento = video_experimento
    db.commit()
    db.refresh(existing_experimento)
    return existing_experimento


@app.delete("/experimentos/{experimento_id}", tags=["Experimentos"])
def delete_experimento(experimento_id: int, db: Session = Depends(get_db)):
    experimento = db.query(Experimento).filter(Experimento.id_experimento == experimento_id).first()
    if not experimento:
        raise HTTPException(status_code=404, detail="Experimento no encontrado")
    db.delete(experimento)
    db.commit()
    return experimento

# Rutas para Preguntas
@app.post("/preguntas/", tags=["Preguntas"])
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


@app.get("/preguntas/", tags=["Preguntas"])
def read_preguntas(db: Session = Depends(get_db)):
    preguntas = db.query(Pregunta).all()
    return preguntas


@app.put("/preguntas/{pregunta_id}", tags=["Preguntas"])
def update_pregunta(
    pregunta_id: int, 
    id_questionario: int, 
    enunciado: str, 
    respuesta: str, 
    correcta: str, 
    respuesta1: str, 
    respuesta2: str, 
    respuesta3: str, 
    db: Session = Depends(get_db)
):
    existing_pregunta = db.query(Pregunta).filter(
        Pregunta.id_pregunta == pregunta_id,
        Pregunta.id_questionario == id_questionario
    ).first()
    if not existing_pregunta:
        raise HTTPException(
            status_code=404, 
            detail="Pregunta no encontrada para el cuestionario especificado"
        )
    existing_pregunta.enunciado = enunciado
    existing_pregunta.respuesta = respuesta
    existing_pregunta.correcta = correcta
    existing_pregunta.respuesta1 = respuesta1
    existing_pregunta.respuesta2 = respuesta2
    existing_pregunta.respuesta3 = respuesta3
    db.commit()
    db.refresh(existing_pregunta)
    return existing_pregunta


@app.delete("/preguntas/{pregunta_id}", tags=["Preguntas"])
def delete_pregunta(pregunta_id: int, db: Session = Depends(get_db)):
    pregunta = db.query(Pregunta).filter(Pregunta.id_pregunta == pregunta_id).first()
    if not pregunta:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    db.delete(pregunta)
    db.commit()
    return pregunta

# Rutas para Clases Usuarios
@app.post("/clases_usuarios/", tags=["Clases Usuarios"])
def create_clase_usuario(id_usuarios: int, id_clases: int, db: Session = Depends(get_db)):
    nueva_clase_usuario = ClaseUsuario(
        id_usuarios=id_usuarios,
        id_clases=id_clases
    )
    db.add(nueva_clase_usuario)
    db.commit()
    return {"message": "Usuario asignado a la clase con éxito"}


@app.get("/clases_usuarios/", tags=["Clases Usuarios"])
def read_clases_usuarios(db: Session = Depends(get_db)):
    clases_usuarios = db.query(ClaseUsuario).all()
    return clases_usuarios


@app.put("/clases_usuarios/{id_usuarios}/{id_clases}", tags=["Clases Usuarios"])
def update_clase_usuario(id_usuarios: int, id_clases: int, new_id_usuarios: int, new_id_clases: int, db: Session = Depends(get_db)):
    existing_clase_usuario = db.query(ClaseUsuario).filter(ClaseUsuario.id_usuarios == id_usuarios, ClaseUsuario.id_clases == id_clases).first()
    if not existing_clase_usuario:
        raise HTTPException(status_code=404, detail="Clase Usuario no encontrada")
    existing_clase_usuario.id_usuarios = new_id_usuarios
    existing_clase_usuario.id_clases = new_id_clases
    db.commit()
    return {"message": "Clase Usuario actualizada con éxito"}


@app.delete("/clases_usuarios/{id_usuarios}/{id_clases}", tags=["Clases Usuarios"])
def delete_clase_usuario(id_usuarios: int, id_clases: int, db: Session = Depends(get_db)):
    clase_usuario = db.query(ClaseUsuario).filter(ClaseUsuario.id_usuarios == id_usuarios, ClaseUsuario.id_clases == id_clases).first()
    if not clase_usuario:
        raise HTTPException(status_code=404, detail="Clase Usuario no encontrada")
    db.delete(clase_usuario)
    db.commit()
    return {"message": "Clase Usuario eliminada con éxito"}

# Rutas para Temarios Cuestionarios
@app.post("/temarios_cuestionarios/", tags=["Temarios Cuestionarios"])
def create_temario_cuestionario(id_clases: int, id_questionario: int, id_temario: int, db: Session = Depends(get_db)):
    nuevo_temario_cuestionario = TemarioCuestionario(
        id_clases=id_clases,
        id_questionario=id_questionario,
        id_temario=id_temario
    )
    db.add(nuevo_temario_cuestionario)
    db.commit()
    return {"message": "Cuestionario asignado al temario con éxito"}


@app.get("/temarios_cuestionarios/", tags=["Temarios Cuestionarios"])
def read_temarios_cuestionarios(db: Session = Depends(get_db)):
    temarios_cuestionarios = db.query(TemarioCuestionario).all()
    return temarios_cuestionarios


@app.put("/temarios_cuestionarios/{id}", tags=["Temarios Cuestionarios"])
def update_temario_cuestionario(id: int, id_clases: int, id_questionario: int, id_temario: int, db: Session = Depends(get_db)):
    existing_temario_cuestionario = db.query(TemarioCuestionario).filter(TemarioCuestionario.id == id).first()
    if not existing_temario_cuestionario:
        raise HTTPException(status_code=404, detail="Temario Cuestionario no encontrado")
    existing_temario_cuestionario.id_clases = id_clases
    existing_temario_cuestionario.id_questionario = id_questionario
    existing_temario_cuestionario.id_temario = id_temario
    db.commit()
    db.refresh(existing_temario_cuestionario)
    return {"message": "Temario Cuestionario actualizado con éxito"}


@app.delete("/temarios_cuestionarios/{id}", tags=["Temarios Cuestionarios"])
def delete_temario_cuestionario(id: int, db: Session = Depends(get_db)):
    temario_cuestionario = db.query(TemarioCuestionario).filter(TemarioCuestionario.id == id).first()
    if not temario_cuestionario:
        raise HTTPException(status_code=404, detail="Temario Cuestionario no encontrado")
    db.delete(temario_cuestionario)
    db.commit()
    return {"message": "Temario Cuestionario eliminado con éxito"}

# Rutas para Videos Experimentos
@app.post("/videos_experimentos/", tags=["Videos Experimentos"])
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


@app.get("/videos_experimentos/", tags=["Videos Experimentos"])
def read_videos_experimentos(db: Session = Depends(get_db)):
    videos_experimentos = db.query(VideoExperimento).all()
    return videos_experimentos


@app.put("/videos_experimentos/{video_id}", tags=["Videos Experimentos"])
def update_video_experimento(video_id: int, id_experimento: int, nombre_experimento: str, descrip_experimento: str, video_experimento: str, db: Session = Depends(get_db)):
    existing_video_experimento = db.query(VideoExperimento).filter(VideoExperimento.id == video_id).first()
    if not existing_video_experimento:
        raise HTTPException(status_code=404, detail="Video Experimento no encontrado")
    existing_video_experimento.id_experimento = id_experimento
    existing_video_experimento.nombre_experimento = nombre_experimento
    existing_video_experimento.descrip_experimento = descrip_experimento
    existing_video_experimento.video_experimento = video_experimento
    db.commit()
    db.refresh(existing_video_experimento)
    return existing_video_experimento


@app.delete("/videos_experimentos/{video_id}", tags=["Videos Experimentos"])
def delete_video_experimento(video_id: int, db: Session = Depends(get_db)):
    video_experimento = db.query(VideoExperimento).filter(VideoExperimento.id == video_id).first()
    if not video_experimento:
        raise HTTPException(status_code=404, detail="Video Experimento no encontrado")
    db.delete(video_experimento)
    db.commit()
    return {"message": "Video Experimento eliminado con éxito"}


# Rutas para Datos Experimentos
@app.post("/datos_experimentos/", tags=["Datos Experimentos"])
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


@app.get("/datos_experimentos/", tags=["Datos Experimentos"])
def read_datos_experimentos(db: Session = Depends(get_db)):
    datos_experimentos = db.query(DatoExperimento).all()
    return datos_experimentos


@app.put("/datos_experimentos/{id_datos}", tags=["Datos Experimentos"])
def update_datos_experimento(id_datos: str, id_experimento: int, masa1: float = None, masa2: float = None, masa3: float = None, masa4: float = None, velocidad1: float = None, velocidad2: float = None, velocidad3: float = None, velocidad4: float = None, velocidad5: float = None, altura1: float = None, altura2: float = None, altura3: float = None, altura4: float = None, tiempo1: float = None, tiempo2: float = None, tiempo3: float = None, tiempo4: float = None, db: Session = Depends(get_db)):
    existing_dato_experimento = db.query(DatoExperimento).filter(DatoExperimento.id_datos == id_datos).first()
    if not existing_dato_experimento:
        raise HTTPException(status_code=404, detail="Dato Experimento no encontrado")
    existing_dato_experimento.id_experimento = id_experimento
    existing_dato_experimento.masa1 = masa1
    existing_dato_experimento.masa2 = masa2
    existing_dato_experimento.masa3 = masa3
    existing_dato_experimento.masa4 = masa4
    existing_dato_experimento.velocidad1 = velocidad1
    existing_dato_experimento.velocidad2 = velocidad2
    existing_dato_experimento.velocidad3 = velocidad3
    existing_dato_experimento.velocidad4 = velocidad4
    existing_dato_experimento.velocidad5 = velocidad5
    existing_dato_experimento.altura1 = altura1
    existing_dato_experimento.altura2 = altura2
    existing_dato_experimento.altura3 = altura3
    existing_dato_experimento.altura4 = altura4
    existing_dato_experimento.tiempo1 = tiempo1
    existing_dato_experimento.tiempo2 = tiempo2
    existing_dato_experimento.tiempo3 = tiempo3
    existing_dato_experimento.tiempo4 = tiempo4
    db.commit()
    db.refresh(existing_dato_experimento)
    return existing_dato_experimento


@app.delete("/datos_experimentos/{id_datos}", tags=["Datos Experimentos"])
def delete_datos_experimento(id_datos: str, db: Session = Depends(get_db)):
    dato_experimento = db.query(DatoExperimento).filter(DatoExperimento.id_datos == id_datos).first()
    if not dato_experimento:
        raise HTTPException(status_code=404, detail="Dato Experimento no encontrado")
    db.delete(dato_experimento)
    db.commit()
    return {"message": "Dato Experimento eliminado con éxito"}

# Rutas para Temarios Experimentos
@app.post("/temarios_experimentos/", tags=["Temarios Experimentos"])
def create_temario_experimento(id_temario: int, id_experimento: int, db: Session = Depends(get_db)):
    nuevo_temario_experimento = TemarioExperimento(
        id_temario=id_temario,
        id_experimento=id_experimento
    )
    db.add(nuevo_temario_experimento)
    db.commit()
    return {"message": "Experimento asignado al temario con éxito"}


@app.get("/temarios_experimentos/", tags=["Temarios Experimentos"])
def read_temarios_experimentos(db: Session = Depends(get_db)):
    temarios_experimentos = db.query(TemarioExperimento).all()
    return temarios_experimentos


@app.put("/temarios_experimentos/{id}", tags=["Temarios Experimentos"])
def update_temario_experimento(id: int, id_temario: int, id_experimento: int, db: Session = Depends(get_db)):
    existing_temario_experimento = db.query(TemarioExperimento).filter(TemarioExperimento.id == id).first()
    if not existing_temario_experimento:
        raise HTTPException(status_code=404, detail="Temario Experimento no encontrado")
    existing_temario_experimento.id_temario = id_temario
    existing_temario_experimento.id_experimento = id_experimento
    db.commit()
    db.refresh(existing_temario_experimento)
    return {"message": "Temario Experimento actualizado con éxito"}

@app.get("/clases/{clase_id}/participantes", response_model=List[UsuarioBase], tags=["Clases"])
def get_participantes_de_clase(clase_id: int, db: Session = Depends(get_db)):
    participantes = (
        db.query(Usuario)
        .join(ClaseUsuario, ClaseUsuario.id_usuarios == Usuario.id_usuarios)
        .filter(ClaseUsuario.id_clases == clase_id)
        .all()
    )
    if not participantes:
        raise HTTPException(status_code=404, detail="No se encontraron participantes para la clase especificada")
    return participantes


@app.delete("/temarios_experimentos/{id}", tags=["Temarios Experimentos"])
def delete_temario_experimento(id: int, db: Session = Depends(get_db)):
    temario_experimento = db.query(TemarioExperimento).filter(TemarioExperimento.id == id).first()
    if not temario_experimento:
        raise HTTPException(status_code=404, detail="Temario Experimento no encontrado")
    db.delete(temario_experimento)
    db.commit()
    return {"message": "Temario Experimento eliminado con éxito"}


@app.get("/health/", response_model=dict, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
