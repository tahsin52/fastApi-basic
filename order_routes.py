from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel, OrderStatusModel
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

    """
    # A sample hello world endpoint
    The endpoint will return a string "Hello World"

    
    :param Authorize:
    :return: Get
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    return {"message": "Hello from order_routes.py"}


@order_router.post("/order", status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, Authorize: AuthJWT = Depends()):

    """
    ## Place an order
    This requires the following parameters:
    - pizza_sizes: str
    - quantity: int

    :param order:
    :param Authorize:
    :return: New order placed by user
    """

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

    """
    ## List all orders
    This list all orders made. It can be accessed by both staff
    - pizza_sizes: str
    - quantity: int

    :param Authorize:
    :return: Get all orders
    """

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

    """
    ## Get an order by id
    This endpoint will return an order by id. It can be accessed by both staff
    - pizza_sizes: str
    - quantity: int

    :param order_id:
    :param Authorize:
    :return: Get an order by id
    """

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

    """
    ## Get all orders made by a user
    This endpoint will return all orders made by a user. It can be accessed by both staff and users
    - pizza_sizes: str
    - quantity: int

    :param Authorize:
    :return: list of orders made by a user
    """

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

    """
    ## Get a specific order made by a user
    This endpoint will return a specific order made by a user. It can be accessed by both staff and users
    - pizza_sizes: str
    - quantity: int

    :param order_id:
    :param Authorize:
    :return: order details or error message if order not found or user is not authorized to view this page or order is not found
    """

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


@order_router.patch('/order/update/{order_id}', status_code=status.HTTP_200_OK)
async def update_order_status(order_id: int, order: OrderStatusModel, Authorize: AuthJWT = Depends()):

    """
    ## Update order status
    This endpoint will update an order's status and requires 'order_status' in str.

    :param order_id:
    :param order:
    :param Authorize:
    :return: updated order status in json format if successful else error message in json format if unsuccessful
    """

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    username = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == username).first()

    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == order_id).first()

        if order_to_update is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found")

        order_to_update.order_status = order.order_status
        order_to_update.pizza_sizes = order.pizza_sizes

        session.commit()

        response = {
            "id": order_to_update.id,
            "pizza_sizes": order_to_update.pizza_sizes,
            "quantity": order_to_update.quantity,
            "order_status": order_to_update.order_status,
        }

        return jsonable_encoder(response)


@order_router.delete('/order/delete/{order_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, Authorize: AuthJWT = Depends()):

    """
    ## Delete an order
    This endpoint will delete an order by id.

    :param order_id:
    :param Authorize:
    :return: None if successful deletion else raise HTTPException with status code 400
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    username = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == username).first()

    if current_user.is_staff:
        order_to_delete = session.query(Order).filter(Order.id == order_id).first()

        if order_to_delete is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found")

        session.delete(order_to_delete)
        session.commit()

        return {"message": "Order deleted successfully", "Order: ": order_to_delete}