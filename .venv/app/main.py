from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, database

# Cria as tabelas automaticamente (Ideal para o início do dev)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="SaaS Core API v1")

@app.get("/")
def health_check():
    return {"status": "online", "version": "1.0.0"}

@app.post("/clients/", response_model=schemas.ClientResponse)
def create_client(client: schemas.ClientCreate, db: Session = Depends(database.get_db)):
    db_client = models.Client(name=client.name, email=client.email)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client