import os
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# URL vinda do .env para segurança
SQLALCHEMY_DATABASE_URL = "postgresql://testa_user:adm123@localhost:5432/earthprayer"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependência para injetar o DB nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()