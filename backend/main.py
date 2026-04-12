import fastapi
from routers.api_routes import router
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()

app.include_router(router)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def __init__():
    print("App initialized")