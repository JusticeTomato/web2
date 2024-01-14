from fastapi import FastAPI, Depends, HTTPException, Request, Form, Path
from sqlalchemy import create_engine, Column, Integer, String, Text, MetaData, DateTime, text
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
