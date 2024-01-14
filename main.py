from fastapi import FastAPI, Depends, HTTPException, Request, Form, Path
from sqlalchemy import create_engine, Column, Integer, String, Text, MetaData, DateTime, text
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

DATABASE_URL = os.getenv("DATABASE_URL")

Base: DeclarativeMeta = declarative_base()
engine = create_engine(DATABASE_URL)
metadata = MetaData()
class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    content = Column(Text)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Dependency to get the database session
async def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

@app.get("/post/{post_id}", response_class=HTMLResponse)
def read_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("post.html", {"request": request, "post": post})

@app.post("/create", response_class=HTMLResponse)
def create_post(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    new_post = Post(title=title, content=content)
    db.add(new_post)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
