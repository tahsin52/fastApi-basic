from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel
from fastapi.exceptions import HTTPException
from fastapi.encoders import jsonable_encoder
from database import Session, engine
from fastapi.encoders import jsonable_encoder

order_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

session = Session(bind=engine)


@order_router.get("/")
async def get_order(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    return {"message": "Hello from order_routes.py"}


@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    new_order = Order(
        pizza_sizes=order.pizza_sizes,
        quantity=order.quantity,
    )

    new_order.user = user

    session.add(new_order)
    session.commit()

    response = {
        "pizza_sizes": new_order.pizza_sizes,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status,
    }

    return jsonable_encoder(response)


@order_router.get("/orders")
async def get_all_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()

        return jsonable_encoder(orders)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view this page")


@order_router.get("/orders/{order_id}", status_code=status.HTTP_200_OK)
async def get_order_by_id(order_id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()

    if user.is_staff:
        order = session.query(Order).filter(Order.id == order_id).first()

        response = {
            "pizza_sizes": order.pizza_sizes,
            "quantity": order.quantity,
            "id": order.id,
            "order_status": order.order_status,
        }

        if order is None:
            return {"message": "Order not found"}

        return jsonable_encoder(response)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view this page")


@order_router.get('/user/orders', status_code=status.HTTP_200_OK)
async def get_user_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    orders = session.query(Order).filter(Order.user_id == current_user.id).all()

    if orders is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have no orders")

    response = [
        {
            "pizza_sizes": order.pizza_sizes,
            "quantity": order.quantity,
            "id": order.id,
            "order_status": order.order_status,
        }
        for order in orders
    ]

    return jsonable_encoder(response)


@order_router.get('/user/order/{order_id}', status_code=status.HTTP_200_OK)
async def get_specific_order(order_id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    order = session.query(Order).filter(Order.id == order_id).first()

    if order is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view this page")

    response = {
        "pizza_sizes": order.pizza_sizes,
        "quantity": order.quantity,
        "id": order.id,
        "order_status": order.order_status,
    }

    return jsonable_encoder(response)
