from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict
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
    
    # Validate payment method
    valid_methods = ["Credit Card", "Debit Card", "Digital Wallet", "PayPal", "Apple Pay", "Google Pay"]
    if payment_data.payment_method not in valid_methods:
        raise HTTPException(status_code=400, detail=f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
    
    # Validate payment amount matches booking total
    if abs(float(payment_data.payment_amount) - float(booking.total_amount)) > 0.01:
        raise HTTPException(status_code=400, detail="Payment amount does not match booking total")
    
    # Simulate payment processing (in real app, integrate with payment gateway)
    # Random success/failure for demonstration
    import random
    payment_success = random.random() > 0.1  # 90% success rate
    
    transaction_id = utils.generate_transaction_id()
    
    # Create payment record
    new_payment = models.Payment(
        booking_id=payment_data.booking_id,
        payment_amount=payment_data.payment_amount,
        payment_method=payment_data.payment_method,
        transaction_id=transaction_id,
        payment_status="Completed" if payment_success else "Failed",
        card_last_four=payment_data.card_last_four if payment_data.payment_method in ["Credit Card", "Debit Card"] else None,
        gateway_response="Payment successful" if payment_success else "Payment declined by gateway"
    )
    db.add(new_payment)
    
    # Update booking status only if payment successful
    if payment_success:
        booking.booking_status = "Confirmed"
    
    db.commit()
    db.refresh(new_payment)
    
    if not payment_success:
        raise HTTPException(
            status_code=402,
            detail={
                "message": "Payment failed. Please try again or use a different payment method.",
                "payment_id": new_payment.payment_id,
                "transaction_id": transaction_id
            }
        )
    
    return {
        "payment_id": new_payment.payment_id,
        "transaction_id": transaction_id,
        "payment_status": "Completed",
        "payment_method": payment_data.payment_method,
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


@router.get("/booking/{booking_id}/history")
def get_payment_history(booking_id: int, db: Session = Depends(database.get_db)):
    """Get all payment attempts for a booking"""
    payments = db.query(models.Payment).filter(
        models.Payment.booking_id == booking_id
    ).order_by(models.Payment.payment_date.desc()).all()
    
    return [
        {
            "payment_id": p.payment_id,
            "payment_amount": float(p.payment_amount),
            "payment_method": p.payment_method,
            "payment_status": p.payment_status,
            "payment_date": str(p.payment_date),
            "transaction_id": p.transaction_id,
            "gateway_response": p.gateway_response
        }
        for p in payments
    ]


@router.post("/{payment_id}/refund")
def process_refund(payment_id: int, db: Session = Depends(database.get_db)):
    """Process refund for a payment"""
    payment = db.query(models.Payment).filter(
        models.Payment.payment_id == payment_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.payment_status != "Completed":
        raise HTTPException(status_code=400, detail="Can only refund completed payments")
    
    if payment.payment_status == "Refunded":
        raise HTTPException(status_code=400, detail="Payment already refunded")
    
    # Get booking
    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == payment.booking_id
    ).first()
    
    # Simulate refund processing
    refund_transaction_id = f"REF-{utils.generate_transaction_id()}"
    
    # Update payment record
    payment.payment_status = "Refunded"
    payment.refund_date = datetime.now()
    payment.refund_transaction_id = refund_transaction_id
    payment.gateway_response = f"{payment.gateway_response} | Refund processed"
    
    # Update booking
    if booking:
        booking.booking_status = "Cancelled"
        booking.cancellation_date = datetime.now()
        booking.refund_amount = payment.payment_amount
        
        # Release seats
        performance = db.query(models.Performance).filter(
            models.Performance.performance_id == booking.performance_id
        ).first()
        
        if performance:
            seat_count = db.query(models.BookingDetail).filter(
                models.BookingDetail.booking_id == booking.booking_id
            ).count()
            performance.available_seats += seat_count
    
    db.commit()
    
    return {
        "message": "Refund processed successfully",
        "refund_transaction_id": refund_transaction_id,
        "refund_amount": float(payment.payment_amount),
        "refund_date": str(payment.refund_date)
    }
