from fastapi import FastAPI
from app.routes import user_routes

app = FastAPI(title="device_systems", version="1.0.0")


@app.middleware("http")
async def add_custom_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"
    return response


app.include_router(user_routes.router)


@app.get("/")
def read_root():
    return {"message": "Bienvenido a device_system API"}