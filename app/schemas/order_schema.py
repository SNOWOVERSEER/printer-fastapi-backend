from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import datetime, timezone
import pytz

target_timezone = pytz.timezone('Australia/Sydney')


class OrderBase(BaseModel):
    file_name: str
    file_id: str
    pages: int
    color_mode: str  # "color" or "bw"
    sides: str  # "single" or "double"
    paper_size: str  # "A4", "A3"
    orientation: str  # "portrait" or "landscape"
    pages_per_side: int = 1
    copies: int = 1
    amount: float
    delivery_method: str  # "pickup" or "delivery"
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    building: Optional[str] = None
    mailbox_number: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: str

class OrderResponseForCreate(BaseModel):
    order_search_id: str
    username: Optional[str] = None
    file_id: str
    status: str
    is_guest: bool
    created_at: datetime

class OrderResponse(OrderBase):
    order_search_id: str
    username: Optional[str] = None
    is_guest: bool
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @field_validator('created_at', 'updated_at', 'completed_at', mode='before')
    def convert_datetime_to_local(cls, value):
        if value is None:
            return None
    
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            
            return value.astimezone(target_timezone)
        return value

    class Config:
        from_attributes = True
    
class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int
    page: int
    size: int
    total_pages: int    