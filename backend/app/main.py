from fastapi import FastAPI, Request, Depends, Form, status, HTTPException,File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine
import os
from fastapi.staticfiles import StaticFiles
from pathlib import Path
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
PROFILE_IMAGES_DIR = Path("app/static/profile_images")
PROFILE_IMAGES_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/login", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username)
    if user and user.password == password:  # En producción, usa un hash para las contraseñas
        # Redirigir al perfil del usuario y establecer una cookie de sesión
        response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="username", value=username)
        return response
    else:
        # Mostrar un mensaje de error si las credenciales son incorrectas
        return templates.TemplateResponse("login.html", {"request": request, "message": "Credenciales incorrectas"})
    

 
@app.get("/logout", response_class=HTMLResponse)
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="username")  # Elimina la cookie de sesión
    return response


# Endpoint para mostrar el formulario de registro
@app.get("/register", response_class=HTMLResponse)
async def show_register_form(request: Request):
    """
    Muestra el formulario de registro.
    """
    return templates.TemplateResponse("register.html", {"request": request, "message": ""})


# Endpoint para procesar el registro de un nuevo usuario
@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    existing_user = crud.get_user_by_username(db, username)
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "message": "El nombre de usuario ya está en uso"})

    # Guardar la imagen de perfil si se proporciona
    profile_image_filename = None
    if profile_image:
        file_extension = profile_image.filename.split(".")[-1]
        profile_image_filename = f"{username}_profile.{file_extension}"
        profile_image_path = f"app/static/profile_images/{profile_image_filename}"

        # Guardar la imagen en el servidor
        with open(profile_image_path, "wb") as buffer:
            buffer.write(await profile_image.read())

    # Crear el usuario en la base de datos
    user = schemas.UserCreate(
        username=username,
        email=email,
        password=password,
        profile_image=profile_image_filename
    )
    crud.create_user(db=db, user=user)

    # Redirigir al usuario a la página de profile
    response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
    return response


# Endpoint para mostrar el formulario de inicio de sesión
@app.get("/login", response_class=HTMLResponse)
async def show_login_form(request: Request):
    """
    Muestra el formulario de inicio de sesión.
    """
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})


# Endpoint para procesar el inicio de sesión
@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Procesa el formulario de inicio de sesión y redirige al perfil del usuario si las credenciales son válidas.
    """
    # Verificar las credenciales del usuario
    user = crud.get_user_by_username(db, username)
    if user and user.password == password:  # En producción, usa un hash para las contraseñas
        # Redirigir al perfil del usuario y establecer una cookie de sesión
        response = RedirectResponse(url="/profile", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="username", value=username)
        return response
    else:
        # Mostrar un mensaje de error si las credenciales son incorrectas
        return templates.TemplateResponse("login.html", {"request": request, "message": "Credenciales incorrectas"})


# Endpoint para mostrar el perfil del usuario
@app.get("/profile", response_class=HTMLResponse)
async def show_profile(request: Request, db: Session = Depends(get_db)):
    # Obtén el nombre de usuario desde la cookie
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Obtén los datos del usuario desde la base de datos
    user = crud.get_user_by_username(db, username)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Renderiza la plantilla de perfil con los datos del usuario
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


# Endpoint para cerrar sesión
@app.get("/logout", response_class=HTMLResponse)
async def logout():
    """
    Cierra la sesión del usuario y redirige a la página principal.
    """
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="username")  # Eliminar la cookie de sesión
    return response