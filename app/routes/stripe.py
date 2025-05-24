from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user_optional
from app.models.user import User
from app.models.order import Order
from app.services.stripe_service import get_stripe_service, StripeService
from typing import Optional

router = APIRouter()

@router.post("/create-checkout-session/{order_id}")
async def create_checkout_session(
    order_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    stripe_service: StripeService = Depends(get_stripe_service),
    db: Session = Depends(get_db)
):
    # get order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    
    if current_user and current_user.id != order.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="no permission to access this order")
    
    # paid order cannot be paid again
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="this order is not pending")
    
    # create payment session
    try:
        checkout_session = await stripe_service.create_checkout_session(order)
        return checkout_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-payment")
async def verify_payment(
    session_id: str = Query(...),
    order_id: str = Query(...),
    current_user: Optional[User] = Depends(get_current_user_optional),
    stripe_service: StripeService = Depends(get_stripe_service),
    db: Session = Depends(get_db)
):
    # get order
    order = db.query(Order).filter(Order.order_search_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="order not found")
    
    
    # verify payment
    try:
        payment_info = await stripe_service.verify_payment(session_id, order_id)
        
        # if payment is successful, update order status
        if payment_info['is_paid'] and order.status == "pending":
            order.status = "processing"
            db.add(order)
            db.commit()
            db.refresh(order)
        
        return payment_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_service: StripeService = Depends(get_stripe_service),
    db: Session = Depends(get_db)
):
    # handle Stripe webhook
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="missing Stripe signature")
    
    try:
        event_info = await stripe_service.handle_webhook(payload, sig_header)
        
        # if payment is successful and there is an order ID
        if event_info.get('is_paid', False) and event_info.get('order_id'):
            order = db.query(Order).filter(Order.id == event_info['order_id']).first()
            if order and order.status == "pending":
                order.status = "processing"
                db.add(order)
                db.commit()
        
        return {"status": "success", "event": event_info.get('event_type')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))