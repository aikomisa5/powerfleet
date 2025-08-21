from typing import List

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, schemas, database, auth_service, brand_service, car_service, picture_service
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi.responses import JSONResponse

app = FastAPI()
print("✅ main.py loaded")

origins = ["*"]  # Cambiar para producción

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

import logging
logger = logging.getLogger("uvicorn.error")


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except IntegrityError as e:
        logger.error(f"Error en endpoint {request.url.path}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={"error": "Violación de integridad en la base de datos", "detail": str(e.orig)}
        )
    except SQLAlchemyError as e:
        logger.error(f"Error en endpoint {request.url.path}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={"error": "Error en la base de datos", "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Error en endpoint {request.url.path}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Error inesperado", "detail": str(e)}
        )

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    access_token = auth_service.create_access_token(data={"sub": user.username, "is_admin": user.is_admin})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=schemas.UserOut)
def register(
        user: schemas.UserCreate,
        current_admin: models.User = Depends(auth_service.get_current_admin_user),  # Only admins can register
        db: Session = Depends(database.get_db)
):
    db_user = auth_service.get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Error: Usuario ya registrado")
    hashed_password = auth_service.get_password_hash(user.password)
    new_user = models.User(username=user.username, password=hashed_password, is_admin=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth_service.get_current_user)):
    return current_user

@app.post("/admin-only-endpoint")
def admin_action(admin_user: models.User = Depends(auth_service.get_current_admin_user)):
    return {"msg": "Solo admins pueden ver esto", "user": admin_user.username}

@app.get("/brands", response_model=List[schemas.BrandOut])
def get_brands(
        db: Session = Depends(database.get_db)
):
    db_brands = brand_service.get_brands(db)
    return db_brands

@app.get("/hello")
def post_hello():
    return {"ok": True}

@app.post("/brands", response_model=schemas.BrandOut)
def post_brand(
        brand: schemas.BrandBase,
        current_admin: models.User = Depends(auth_service.get_current_admin_user),
        db: Session = Depends(database.get_db)
):
    try:
        filters = {
            "name": brand.name
        }
        db_brand = brand_service.get_brands(db, filters)
        if db_brand:
            raise HTTPException(status_code=400, detail="Error: Marca de auto ya registrada")
        new_brand = brand_service.post_brand(db, brand.name)
        return new_brand
    except Exception as e:
        print(f"Internal error {e}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@app.get("/brands/{id_brand}/cars", response_model=List[schemas.CarOut])
def get_cars(
        id_brand: int,
        db: Session = Depends(database.get_db)
):
    filters = {
        "id_brand": id_brand
    }
    db_cars = car_service.get_cars(db, filters)
    return db_cars

@app.post("/brands/{id_brand}/cars", response_model=schemas.CarOut)
def post_car(
        car: schemas.CarCreate,
        id_brand: int,
        current_admin: models.User = Depends(auth_service.get_current_admin_user),
        db: Session = Depends(database.get_db)
):
    filters = {
        "model": car.model
    }
    db_cars = car_service.get_cars(db, filters)
    if db_cars:
        raise HTTPException(status_code=400, detail="Error: Modelo de auto ya registrado")
    new_car = car_service.post_car(db, id_brand=id_brand, model=car.model)
    return new_car

@app.get("/brands/{id_brand}/cars/{id_car}/pictures", response_model=List[schemas.PictureOut])
def get_pictures(
        id_brand: int,
        id_car: int,
        db: Session = Depends(database.get_db)
):
    filters = {
        "id_car": id_car
    }
    db_pictures = picture_service.get_pictures(db, filters)
    return db_pictures

@app.post("/brands/{id_brand}/cars/{id_car}/pictures", response_model=schemas.PictureOut)
def post_picture(
        picture: schemas.PictureCreate,
        id_brand: int,
        id_car: int,
        current_admin: models.User = Depends(auth_service.get_current_admin_user),
        db: Session = Depends(database.get_db)
):
    try:
        new_picture = picture_service.post_picture(
            db,
            id_car=id_car,
            description=picture.description,
            url=picture.url
        )
        return new_picture
    except Exception as e:
        print(f"Internal error {e}")
        raise HTTPException(status_code=500, detail="Something went wrong")


@app.get("/brands/{id_brand}/cars/{id_car}/pictures/{url}")
def get_picture_raw(
        url: str,
        current_admin: models.User = Depends(auth_service.get_current_admin_user),  # Only admins can register
):
    return picture_service.get_picture_raw(url)
