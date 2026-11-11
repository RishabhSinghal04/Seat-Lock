from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post(path="signup")
def signup():
    pass

@auth_router.post(path="login")
def login():
    pass
