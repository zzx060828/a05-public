# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.datebase import get_db
from ...models.user import EnterpriseUser
from ...schemas.user import UserRegisterRequest, UserLoginRequest, TokenResponse, UserOutResponse
from ...core.security import get_password_hash, verify_password, create_access_token
from ...api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["企业账号与鉴权"])


@router.post("/register", response_model=UserOutResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(EnterpriseUser).filter(EnterpriseUser.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    new_user = EnterpriseUser(
        company_name=user_in.company_name,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user_in: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(EnterpriseUser).filter(EnterpriseUser.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    access_token = create_access_token(data={"sub": str(user.id), "role": "enterprise"})
    return {"access_token": access_token, "token_type": "bearer", "role": "enterprise"}


@router.get("/me", response_model=UserOutResponse)
def get_me(current_user: EnterpriseUser = Depends(get_current_user)):
    return current_user
