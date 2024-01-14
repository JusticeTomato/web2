from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
# import logging

# # 로그 설정
# logging.basicConfig(filename='app.log',
#                     level=logging.DEBUG,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class PostDB(Base):
  __tablename__ = "posts"

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String, index=True)
  content = Column(String)
  created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


Base.metadata.create_all(bind=engine)

app = FastAPI(force_https=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="./templates")


class PostForm(BaseModel):
  title: str
  content: str


# db = SessionLocal()
# db.add_all([
#     PostDB(title="one", content="oneone"),
#     PostDB(title="two", content="twotwo"),
#     PostDB(title="three", content="threethree"),
# ])
# db.commit()
# db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
  db = SessionLocal()
  posts = db.query(PostDB).all()
  db.close()

  post_links = [{"id": post.id, "title": post.title} for post in posts]

  return templates.TemplateResponse("index.html", context={
      "request": request,
      "posts": post_links
  })


@app.post("/create", response_class=HTMLResponse)
def create_post(request: Request, title:str=Form(...), content:str=Form(...)):
  
  db = SessionLocal()
  new_post = PostDB(title=title, content=content)
  db.add(new_post)
  db.commit()
  # db.close()
  # 추가된 게시글을 가져와서 출력
  added_post = db.query(PostDB).filter(PostDB.id == new_post.id).first()
  db.close()

  return {"created_post": added_post}
  # return RedirectResponse(url="/", status_code=303)

@app.get("/create", response_class=HTMLResponse)
def create_form(request: Request):
  return read_root(request)


@app.get("/post/{post_id}", response_class=HTMLResponse, name="read_post")
def read_post(request: Request, post_id: int):
    db = SessionLocal()
    post = db.query(PostDB).filter(PostDB.id == post_id).first()
    db.close()

    return templates.TemplateResponse("post.html", {"request": request, "post": post})

if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="0.0.0.0", port=3000)
