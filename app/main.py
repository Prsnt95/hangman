from fastapi import FastAPI

from app.middleware import setup_middleware
from app.routes import router

app=FastAPI()

#set up middleware
setup_middleware(app)

app.include_router(router)


#create routes


