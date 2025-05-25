from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user, get_current_user_optional, is_admin
from app.models.user import User
from app.models.order import Order
from app.schemas.order_schema import OrderCreate, OrderResponse, OrderUpdate, OrderResponseForCreate


router = APIRouter()

@router.post("", response_model=OrderResponseForCreate)
async def create_order(
    order_in: OrderCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    random_num = str(uuid.uuid4().int)[:4]
    order_search_id = f"{timestamp}-{random_num}"
    order = Order(
        id=str(uuid.uuid4()),
        file_id=order_in.file_id,
        file_name=order_in.file_name,
        pages=order_in.pages,
        color_mode=order_in.color_mode,
        sides=order_in.sides,
        paper_size=order_in.paper_size,
        orientation=order_in.orientation,
        pages_per_side=order_in.pages_per_side,
        copies=order_in.copies,
        amount=order_in.amount,
        delivery_method=order_in.delivery_method,
        email=order_in.email,
        name=order_in.name,
        phone=order_in.phone,
        building=order_in.building,
        mailbox_number=order_in.mailbox_number,
        notes=order_in.notes,
        status="pending",
        order_search_id=order_search_id
    )
    
    if current_user:
        order.user_id = current_user.id
        order.username = current_user.username
        order.is_guest = False
    else:
        order.is_guest = True
    
    db.add(order)
    db.commit()
    db.refresh(order)
    return {
        "order_search_id": order.order_search_id,
        "username": order.username,
        "file_id": order.file_id,
        "status": order.status,
        "is_guest": order.is_guest,
        "created_at": order.created_at
    }

@router.get("/my", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return orders

@router.get("/{order_search_id}", response_model=OrderResponse)
async def get_order(
    order_search_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):

    order = db.query(Order).filter(Order.order_search_id == order_search_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    
    if current_user and current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="no permission to view this order")
    
    return order

@router.get("/search/phone/{phone}", response_model=List[OrderResponse])
async def get_orders_by_phone(
    phone: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    orders = db.query(Order).filter(Order.phone == phone).all()
    if current_user and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="no permission to view this order")
    
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this phone number")
    return orders

@router.get("/search/{order_search_id}", response_model=OrderResponse)
async def get_order_by_search_id(
    order_search_id: str,
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(Order.order_search_id == order_search_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    return order

# update order status (only for admin)
@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderUpdate,
    _: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
    
    order = db.query(Order).filter(Order.order_search_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    
    order.status = status_update.status
    if status_update.status == "completed":
        order.completed_at = datetime.now()
    
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

# Get all orders (only for admin)
@router.get("", response_model=List[OrderResponse])
async def get_all_orders(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    _: User = Depends(is_admin),
    db: Session = Depends(get_db)
):
  
    orders = db.query(Order).offset((page - 1) * size).limit(size).all()
    return orders