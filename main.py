from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime
import uvicorn

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

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
