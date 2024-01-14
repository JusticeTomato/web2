from fastapi import FastAPI, Depends, HTTPException, Request, Form
from sqlalchemy import create_engine, Column, Integer, String, Text, MetaData, DateTime, text
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.ext.declarative import DeclarativeMeta
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
