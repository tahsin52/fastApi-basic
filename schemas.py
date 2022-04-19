from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "test",
                "email": "test@test.com",
                "password": "testSecret",
                "is_staff": False,
                "is_active": True
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = '3023b4d8ed3a0b37f84dfd542c6dd82dd515ffa14a4bc423feba19e4f54976d1'


class LoginModel(BaseModel):
    username: str
    password: str

    # class Config:
    #     orm_mode = True
    #     schema_extra = {
    #         "example": {
    #             "username": "test",
    #             "password": "testSecret"
    #         }
    #     }


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: Optional[int]
    order_status: Optional[str] = "pending"
    pizza_sizes: Optional[str] = "small"

    user_id: Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "quantity": 2,
                "pizza_sizes": "large"
            }
        }
