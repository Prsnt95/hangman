from fastapi import FastAPI
from app.middleware import setup_middleware
from app.routes import router

# Create the app instance ONCE
app = FastAPI()

# Set up middleware
setup_middleware(app)

# Include your router
app.include_router(router)