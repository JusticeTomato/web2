from fastapi import FastAPI, Depends, HTTPException, Request, Form, Path
from sqlalchemy import create_engine, Column, Integer, String, Text, MetaData, DateTime, text
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
cache = {}
def get_template(template_name: str, context: dict):
    if template_name in cache:
        return cache[template_name]

    template = templates.TemplateResponse(template_name, context)
    cache[template_name] = template
    return template

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
app.mount("/static", StaticFiles(directory="static"), name="static")

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
    return get_template("index.html", {"request": request, "posts": posts})
    # return templates.TemplateResponse("index.html", {"request": request, "posts": posts})

@app.get("/post/{post_id}", response_class=HTMLResponse)
def read_post(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return get_template("post.html", {"request": request, "post": post})
    # return templates.TemplateResponse("post.html", {"request": request, "post": post})

@app.post("/create", response_class=HTMLResponse)
def create_post(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    new_post = Post(title=title, content=content)
    db.add(new_post)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()

    return RedirectResponse(url="/", status_code=303)
    
# 게시물 수정 페이지 보여주기
@app.get("/edit/{post_id}")
def edit_post_page(post_id: int, request: Request, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return templates.TemplateResponse("edit_post.html", {"request": request, "post": post})

# 게시물 수정 처리
@app.post("/edit/{post_id}")
async def edit_post(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # 게시물 수정
    post.title = title
    post.content = content
    db.commit()

    return RedirectResponse(url=f"/post/{post_id}", status_code=303)
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# if __name__ == "__main__":
#   import uvicorn

#   uvicorn.run(app, host="0.0.0.0", port=3000)
