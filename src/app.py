from fastapi import FastAPI

from .repositories.database import Base, engine
from .routers import security, user_management

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(security.router)
app.include_router(user_management.router)