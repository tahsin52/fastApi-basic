from fastapi import APIRouter, status, Depends
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT

from database import Session, engine
from schemas import *
from models import User, Order
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

session = Session(bind=engine)


@auth_router.get("/")
async def get_auth(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token")

    return {"message": "Hello from auth_routes.py"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User.email).filter(User.email == user.email).first()

    if db_email:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Email already exists")

    db_username = session.query(User.username).filter(User.username == user.username).first()

    if db_username:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="Username already exists")

    new_user = User(
        email=user.email,
        username=user.username,
        password_hash=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )
    session.add(new_user)
    session.commit()

    return new_user


# login route

@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: LoginModel, Authorize: AuthJWT = Depends()):
    db_user = session.query(User).filter(User.username == user.username).first()

    if db_user and check_password_hash(db_user.password_hash, user.password):
        access_token = Authorize.create_access_token(subject=db_user.username)
        refresh_token = Authorize.create_refresh_token(subject=db_user.username)

        response_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

        return jsonable_encoder(response_data)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect username or password")


# refresh token route

@auth_router.get("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Please provide a valid refresh Token")

    current_user = Authorize.get_jwt_subject()

    access_token = Authorize.create_access_token(subject=current_user)

    return jsonable_encoder({"access_token": access_token})
