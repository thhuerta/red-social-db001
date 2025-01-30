from fastapi import FastAPI, Request, Depends, Form, status, HTTPException, File, UploadFile, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from . import models, schemas, crud
from .database import SessionLocal, engine

# Inicializar la base de datos
models.Base.metadata.create_all(bind=engine)

# Configuración de FastAPI y archivos estáticos
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Directorio para imágenes de perfil
PROFILE_IMAGES_DIR = Path("app/static/profile_images")
PROFILE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de plantillas Jinja2
templates = Jinja2Templates(directory="app/templates")

# Dependencia para la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para obtener el usuario autenticado desde la cookie
def get_current_user(username: str = Cookie(None), db: Session = Depends(get_db)):
    if not username:
        return None
    return crud.get_user_by_username(db, username)

# Ruta principal
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(get_current_user)):
    posts = crud.get_posts(db)
    users_to_follow = crud.get_users_to_follow(db, user.id)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "posts": posts,
        "users_to_follow": users_to_follow,
        "user": user
    })

# Mostrar formulario de registro
@app.get("/register", response_class=HTMLResponse)
async def show_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "message": ""})

# Procesar registro de usuario
@app.post("/register", response_class=RedirectResponse)
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    if crud.get_user_by_username(db, username):
        return templates.TemplateResponse("register.html", {"request": request, "message": "El usuario ya existe"})

    profile_image_filename = None
    if profile_image:
        file_extension = profile_image.filename.split(".")[-1]
        profile_image_filename = f"{username}_profile.{file_extension}"
        profile_image_path = PROFILE_IMAGES_DIR / profile_image_filename
        with open(profile_image_path, "wb") as buffer:
            buffer.write(await profile_image.read())

    user = schemas.UserCreate(username=username, email=email, password=password, profile_image=profile_image_filename)
    crud.create_user(db, user)
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return response

# Mostrar formulario de inicio de sesión
@app.get("/login", response_class=HTMLResponse)
async def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})

# Procesar inicio de sesión
@app.post("/login", response_class=RedirectResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_username(db, username)
    if user and user.password == password:
        response = RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="username", value=username)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "message": "Credenciales incorrectas"})

# Mostrar perfil de usuario
@app.get("/profile", response_class=HTMLResponse)
async def show_profile(request: Request, user: schemas.User = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})

# Cerrar sesión
@app.get("/logout", response_class=RedirectResponse)
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="username")
    return response

# Crear post
@app.post("/create_post", response_class=RedirectResponse)
async def create_post(
    request: Request,
    content: str = Form(...),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    post = schemas.PostCreate(content=content)
    crud.create_post(db, post, user.id)
    return RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)

# Agregar comentario
@app.post("/add_comment/{post_id}", response_class=RedirectResponse)
async def add_comment(
    request: Request,
    post_id: int,
    content: str = Form(...),
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    comment = schemas.CommentCreate(content=content, post_id=post_id)
    crud.create_comment(db, comment, user.id)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# Dar like a un post
@app.post("/like_post/{post_id}", response_class=RedirectResponse)
async def like_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    like = schemas.LikeCreate(post_id=post_id)
    crud.create_like(db, like, user.id)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# Seguir a un usuario
@app.post("/follow_user/{user_id}", response_class=RedirectResponse)
async def follow_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    user: schemas.User = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    follow = schemas.FollowerCreate(followed_id=user_id)
    crud.create_follower(db, follow, user.id)
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

