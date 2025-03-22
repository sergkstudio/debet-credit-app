from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import jwt
from passlib.context import CryptContext
from . import models, database, netbird
from pydantic import BaseModel
import os

app = FastAPI(title="VPN Billing System")

# Настройки безопасности
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # В продакшене использовать переменную окружения
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Настройки статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic модели
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    is_admin: bool = False

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class SubscriptionBase(BaseModel):
    netbird_user_id: str
    start_date: datetime
    end_date: datetime

class SubscriptionCreate(SubscriptionBase):
    user_id: int

class Subscription(SubscriptionBase):
    id: int
    status: str
    user_id: int

    class Config:
        from_attributes = True

# Вспомогательные функции
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except jwt.JWTError:
        return None
    
    user = db.query(models.User).filter(models.User.email == email).first()
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Веб-маршруты
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    # Проверяем, существует ли пользователь
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Пользователь с таким email уже существует"
            }
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(password)
    db_user = models.User(
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    
    # Перенаправляем на страницу входа
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неверный email или пароль"
            }
        )
    
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token)
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="access_token")
    return response

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(database.get_db)
):
    subscriptions = db.query(models.Subscription).filter(
        models.Subscription.user_id == current_user.id
    ).all()
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": current_user,
            "subscriptions": subscriptions
        }
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(database.get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    users = db.query(models.User).all()
    subscriptions = db.query(models.Subscription).all()
    
    # Статистика
    stats = {
        "total_users": len(users),
        "active_subscriptions": len([s for s in subscriptions if s.status == "active"]),
        "expiring_subscriptions": len([s for s in subscriptions if s.status == "active" and s.end_date <= datetime.utcnow() + timedelta(days=7)]),
        "blocked_users": len([u for u in users if not u.is_active])
    }
    
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": current_user,
            "users": users,
            "subscriptions": subscriptions,
            "stats": stats
        }
    )

# API маршруты
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/subscriptions/", response_model=Subscription)
def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(database.get_db)
):
    db_subscription = models.Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@app.get("/subscriptions/check-expired")
def check_expired_subscriptions(db: Session = Depends(database.get_db)):
    netbird_api = netbird.NetbirdAPI()
    expired_subs = db.query(models.Subscription).filter(
        models.Subscription.end_date <= datetime.utcnow(),
        models.Subscription.status == "active"
    ).all()
    
    for sub in expired_subs:
        sub.status = "expired"
        netbird_api.block_user(sub.netbird_user_id)
    
    db.commit()
    return {"message": f"Checked {len(expired_subs)} subscriptions"}

@app.get("/subscriptions/{user_id}", response_model=List[Subscription])
def get_user_subscriptions(user_id: int, db: Session = Depends(database.get_db)):
    subscriptions = db.query(models.Subscription).filter(
        models.Subscription.user_id == user_id
    ).all()
    return subscriptions 