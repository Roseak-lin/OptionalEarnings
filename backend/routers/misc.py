from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/")
def root_endpoint():
    return {"message": "Hello, World!"}