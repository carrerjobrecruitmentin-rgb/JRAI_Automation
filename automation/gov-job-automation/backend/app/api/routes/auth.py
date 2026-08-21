from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, create_access_token
from pydantic import BaseModel

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Mock authentication for now. In production, verify against DB.
    if form_data.username == "admin" and form_data.password == "admin123":
        access_token = create_access_token(subject=form_data.username)
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
