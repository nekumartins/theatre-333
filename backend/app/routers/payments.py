from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, database, utils

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def process_payment(
    payment_data: schemas.PaymentCreate,
    db: Session = Depends(database.get_db)
):
    """Process payment for a booking"""
    # Validate booking exists
    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == payment_data.booking_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.booking_status == "Confirmed":
        raise HTTPException(status_code=400, detail="Booking already paid")
    
    # Simulate payment processing (in real app, integrate with payment gateway)
    transaction_id = utils.generate_transaction_id()
    
    # Create payment record
    new_payment = models.Payment(
        booking_id=payment_data.booking_id,
        payment_amount=payment_data.payment_amount,
        payment_method=payment_data.payment_method,
        transaction_id=transaction_id,
        payment_status="Completed",
        card_last_four=payment_data.card_last_four,
        gateway_response="Payment successful"
    )
    db.add(new_payment)
    
    # Update booking status
    booking.booking_status = "Confirmed"
    
    db.commit()
    db.refresh(new_payment)
    
    return {
        "payment_id": new_payment.payment_id,
        "transaction_id": transaction_id,
        "payment_status": "Completed",
        "message": "Payment processed successfully"
    }


@router.get("/{payment_id}", response_model=schemas.PaymentResponse)
def get_payment_detail(payment_id: int, db: Session = Depends(database.get_db)):
    """Get payment details"""
    payment = db.query(models.Payment).filter(
        models.Payment.payment_id == payment_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return payment


@router.get("/booking/{booking_id}", response_model=schemas.PaymentResponse)
def get_payment_by_booking(booking_id: int, db: Session = Depends(database.get_db)):
    """Get payment for a specific booking"""
    payment = db.query(models.Payment).filter(
        models.Payment.booking_id == booking_id,
        models.Payment.payment_status == "Completed"
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="No completed payment found for this booking")
    
    return payment
