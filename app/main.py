from fastapi import FastAPI

from app.middleware import setup_middleware
from app.routes import router
# from app.routes import game

app=FastAPI()

#set up middleware
setup_middleware(app)

# app.include_router(router)

#create routes



app = FastAPI()

app.include_router(router)

