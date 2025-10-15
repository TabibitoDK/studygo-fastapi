import os
from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from .config import settings
from .database import engine, init_db
from .models import User, Post, Progress
from .schemas import (
    RegisterIn, LoginIn, UserOut, UserUpdateIn,
    PostCreateIn, PostOut, ProgressIn, ProgressOut,
)
from .auth import create_token, auth_user, hash_password, verify_password

app = FastAPI(title="StudyGo API (FastAPI)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGIN] if settings.CORS_ORIGIN != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploads
UPLOAD_DIR = settings.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

@app.on_event("startup")
def on_startup():
    init_db()

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/")
def root():
    return {"ok": True, "service": "studygo-fastapi"}

# ---------- Auth ----------
@app.post("/api/register")
def register(payload: RegisterIn, session: Session = Depends(get_session)):
    exists_email = session.exec(select(User).where(User.email == payload.email)).first()
    if exists_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    exists_username = session.exec(select(User).where(User.username == payload.username)).first()
    if exists_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id}

@app.post("/api/login")
def login(payload: LoginIn, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid login")
    token = create_token(user.id, user.username)
    return {"token": token}

# ---------- Users ----------
@app.get("/api/me", response_model=UserOut)
def me(claims=Depends(auth_user), session: Session = Depends(get_session)):
    user = session.get(User, claims["uid"])
    return user

@app.patch("/api/me", response_model=UserOut)
def update_me(data: UserUpdateIn, claims=Depends(auth_user), session: Session = Depends(get_session)):
    user = session.get(User, claims["uid"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.bio is not None:
        user.bio = data.bio
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    if data.background_url is not None:
        user.background_url = data.background_url
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# ---------- Uploads ----------
@app.post("/api/upload")
def upload_file(file: UploadFile = File(...), claims=Depends(auth_user)):
    # simple save; sanitize name in production
    ext = os.path.splitext(file.filename)[1]
    name = f"{int(datetime.utcnow().timestamp()*1000)}_{os.urandom(4).hex()}{ext}"
    outpath = os.path.join(UPLOAD_DIR, name)
    with open(outpath, "wb") as f:
        f.write(file.file.read())
    url = f"{settings.BASE_URL}/files/{name}"
    return {"url": url}

# ---------- Posts ----------
@app.get("/api/posts", response_model=List[PostOut])
def list_posts(session: Session = Depends(get_session)):
    posts = session.exec(select(Post).order_by(Post.created_at.desc()).limit(50)).all()
    return posts

@app.post("/api/posts", response_model=PostOut)
def create_post(payload: PostCreateIn, claims=Depends(auth_user), session: Session = Depends(get_session)):
    post = Post(user_id=claims["uid"], content=payload.content)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: str, claims=Depends(auth_user), session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Not found")
    if post.user_id != claims["uid"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    session.delete(post)
    session.commit()
    return {"ok": True}

# ---------- Progress ----------
@app.get("/api/progress", response_model=List[ProgressOut])
def get_progress(claims=Depends(auth_user), session: Session = Depends(get_session)):
    rows = session.exec(select(Progress).where(Progress.user_id == claims["uid"]).order_by(Progress.updated_at.desc())).all()
    return rows

@app.post("/api/progress", response_model=ProgressOut)
def upsert_progress(payload: ProgressIn, claims=Depends(auth_user), session: Session = Depends(get_session)):
    row = session.exec(
        select(Progress).where(Progress.user_id == claims["uid"], Progress.module == payload.module)
    ).first()

    if row:
        row.percent = payload.percent
        row.updated_at = datetime.utcnow()
        session.add(row)
        session.commit()
        session.refresh(row)
        return row
    else:
        row = Progress(user_id=claims["uid"], module=payload.module, percent=payload.percent)
        session.add(row)
        session.commit()
        session.refresh(row)
        return row
