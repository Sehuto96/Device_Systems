from fastapi import FastAPI
from app.routes import user_routes

app = FastAPI(title="device_systems", version="1.0.0")
app.include_router(user_routes.router)


@app.get("/")
def read_root():
    return {"message": "Bienvenido a device_system API"}