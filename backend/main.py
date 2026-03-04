import fastapi
from routers.api_routes import router

app = fastapi.FastAPI()

app.include_router(router)

def __init__():
    print("App initialized")