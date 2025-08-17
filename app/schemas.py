from pydantic import BaseModel

class PictureBase(BaseModel):
    id_car: int
    description: str
    url: str

class PictureCreate(BaseModel):
    description: str
    url: str

class PictureOut(PictureBase):
    id: int

    class Config:
        orm_mode = True

class CarBase(BaseModel):
    id_brand: int
    model: str

class CarCreate(BaseModel):
    model: str

class CarOut(CarBase):
    id: int

    class Config:
        orm_mode = True

class BrandBase(BaseModel):
    name: str

class BrandCreate(BrandBase):
    pass

class BrandOut(BrandBase):
    id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
