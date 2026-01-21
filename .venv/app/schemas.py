from pydantic import BaseModel, EmailStr

class ClientBase(BaseModel):
    name: str
    email: EmailStr

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True