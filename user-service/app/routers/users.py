from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from app import models,schemas,auth
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session

router=APIRouter(prefix="/users",tags=["users"])

@router.post("/register",response_model=schemas.UserResponse)
async def register(data:schemas.UserCreate,session:AsyncSession=Depends(get_async_session)):
    result= await session.execute(select(models.User).where(models.User.email==data.email))
    existing_user=result.scalar_one_or_none()
    if existing_user: 
        raise HTTPException(status_code=409)
    hashed_password=auth.hash_password(data.password)
    user=models.User(username=data.username,email=data.email,password=hashed_password)
    session.add(user)
    await session.commit()
    return user


@router.post("/login",response_model=schemas.Token)
async def login(data:schemas.UserLogin,session:AsyncSession=Depends(get_async_session)):
    result= await session.execute(select(models.User).where(models.User.email==data.email))
    existing_user=result.scalar_one_or_none()
    if not existing_user: 
        raise HTTPException(status_code=404)
    if not auth.veryfy_password(data.password,existing_user.password):
        raise HTTPException(status_code=401)
    token = auth.create_access_token({"sub": existing_user.email, "user_id": str(existing_user.id)})
    return {"access_token": token, "token_type": "bearer"}
