from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    order_search_id = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String)
    email = Column(String, nullable=False)
    name = Column(String)
    phone = Column(String)
    is_guest = Column(Boolean, default=False)
    
    file_name = Column(String, nullable=False)
    file_id = Column(String, nullable=False)
    pages = Column(Integer, nullable=False)
    

    color_mode = Column(String, nullable=False)  # color or bw
    sides = Column(String, nullable=False)  # single or double
    paper_size = Column(String, nullable=False)  # A4, A3
    orientation = Column(String, nullable=False)  # portrait or landscape
    pages_per_side = Column(Integer, default=1)
    copies = Column(Integer, default=1)
    
    # payment info
    amount = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, cancelled
    
    # delivery info
    delivery_method = Column(String)  # pickup or delivery
    building = Column(String)
    mailbox_number = Column(String)
    notes = Column(String)
    
    # time info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)