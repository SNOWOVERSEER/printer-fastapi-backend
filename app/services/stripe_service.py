import stripe
from app.core.config import settings
from app.models.order import Order
from typing import Dict, Any

class StripeService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    async def create_checkout_session(self, order: Order) -> Dict[str, Any]:
        try:
            line_items = [{
                'price_data': {
                    'currency': 'cny',
                    'product_data': {
                        'name': f'Print Order #{order.id}',
                        'description': f'Print Service: {order.pages} pages, {order.copies} copies, {"Color" if order.color_mode == "color" else "Black & White"}',
                    },
                    'unit_amount': int(order.amount * 100),
                },
                'quantity': 1,
            }]
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/orders/{order.id}?payment_success=true",
                cancel_url=f"{settings.FRONTEND_URL}/orders/{order.id}?payment_canceled=true",
                client_reference_id=order.id,
                customer_email=order.email,
                metadata={
                    'order_id': order.id,
                }
            )
            
            return {
                'session_id': checkout_session.id,
                'url': checkout_session.url
            }
            
        except Exception as e:
            raise Exception(f"Stripe checkout session creation failed: {str(e)}")
    
    async def verify_payment(self, session_id: str, order_id: str) -> Dict[str, Any]:
        try:
            print(f"Verifying payment for session: {session_id}")
            print(f"Order ID: {order_id}")
            print(f"Using Stripe API key: {stripe.api_key[:10]}...") 
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.metadata.get('order_id') != order_id:
                print(f"Payment session does not match order: {session.metadata.get('order_id')} != {order_id}")
                raise Exception("Payment session does not match order")
            
            payment_status = session.payment_status
            print(f"Payment status: {payment_status}")
            return {
                'order_id': order_id,
                'payment_status': payment_status,
                'is_paid': payment_status == 'paid',
                'session_id': session_id
            }
            
        except Exception as e:
            raise Exception(f"Payment verification failed: {str(e)}")
    
    async def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.STRIPE_WEBHOOK_SECRET
            )
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                order_id = session.metadata.get('order_id')
                
                return {
                    'event_type': event['type'],
                    'order_id': order_id,
                    'payment_status': session.payment_status,
                    'is_paid': session.payment_status == 'paid'
                }
            
            return {'event_type': event['type']}
            
        except Exception as e:
            raise Exception(f"Failed to handle webhook: {str(e)}")

stripe_service = StripeService()

def get_stripe_service():
    return stripe_service