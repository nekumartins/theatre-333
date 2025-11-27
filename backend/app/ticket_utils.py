"""
Ticket generation and email utilities for the theatre booking system
Implements business requirements:
- QR code/barcode generation for ticket validation
- Email confirmation with booking details
"""

import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
import random
import string


def generate_booking_reference() -> str:
    """
    Generate unique alphanumeric booking reference
    Format: THR-YYYYMMDD-XXXXX (e.g., THR-20251126-A3B9C)
    """
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"THR-{date_part}-{random_part}"


def generate_qr_code(booking_reference: str, booking_id: int) -> str:
    """
    Generate QR code for booking/ticket validation
    Returns base64 encoded PNG image
    
    Business requirement: QR code for ticket validation at venue
    """
    # QR code data contains booking reference and ID for validation
    qr_data = f"THEATRE_BOOKING:{booking_reference}:{booking_id}"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 string for embedding in emails/web pages
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def calculate_payment_deadline() -> datetime:
    """
    Calculate payment deadline (15 minutes from booking creation)
    
    Business requirement: Bookings must be completed within 15 minutes or released
    
    Note: Using datetime.now() (local time) instead of datetime.utcnow() 
    to match frontend JavaScript Date() which uses local time.
    """
    return datetime.now() + timedelta(minutes=15)


def format_booking_email(booking_data: dict, qr_code_base64: str) -> str:
    """
    Format booking confirmation email with all details and QR code
    
    Business requirement: Email confirmation with booking details and QR code
    
    Args:
        booking_data: Dict containing booking, performance, show, user, and seats info
        qr_code_base64: Base64 encoded QR code image
    
    Returns:
        HTML email content
    """
    email_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; }}
            .ticket {{ background: white; border: 2px solid #667eea; border-radius: 10px; padding: 20px; margin: 20px 0; }}
            .qr-code {{ text-align: center; margin: 20px 0; }}
            .qr-code img {{ max-width: 200px; }}
            .details {{ margin: 20px 0; }}
            .detail-row {{ display: flex; padding: 10px 0; border-bottom: 1px solid #eee; }}
            .detail-label {{ font-weight: bold; width: 150px; }}
            .detail-value {{ flex: 1; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            .seats {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎭 Booking Confirmed!</h1>
                <p>Thank you for your booking</p>
            </div>
            
            <div class="content">
                <div class="ticket">
                    <h2>Booking Reference: {booking_data.get('booking_reference', 'N/A')}</h2>
                    
                    <div class="qr-code">
                        <img src="{qr_code_base64}" alt="QR Code">
                        <p><small>Present this QR code at the venue</small></p>
                    </div>
                    
                    <div class="details">
                        <h3>Show Details</h3>
                        <div class="detail-row">
                            <div class="detail-label">Show:</div>
                            <div class="detail-value">{booking_data.get('show_title', 'N/A')}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Date:</div>
                            <div class="detail-value">{booking_data.get('performance_date', 'N/A')}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Time:</div>
                            <div class="detail-value">{booking_data.get('start_time', 'N/A')}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Venue:</div>
                            <div class="detail-value">{booking_data.get('venue_name', 'N/A')}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Venue Address:</div>
                            <div class="detail-value">{booking_data.get('venue_address', 'N/A')}</div>
                        </div>
                    </div>
                    
                    <div class="seats">
                        <h3>Your Seats</h3>
                        <p><strong>{booking_data.get('seat_info', 'N/A')}</strong></p>
                    </div>
                    
                    <div class="details">
                        <h3>Payment Details</h3>
                        <div class="detail-row">
                            <div class="detail-label">Total Amount:</div>
                            <div class="detail-value"><strong>${booking_data.get('total_amount', '0.00')}</strong></div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Payment Status:</div>
                            <div class="detail-value">{booking_data.get('payment_status', 'Confirmed')}</div>
                        </div>
                        <div class="detail-row">
                            <div class="detail-label">Booking Date:</div>
                            <div class="detail-value">{booking_data.get('booking_date', 'N/A')}</div>
                        </div>
                    </div>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <h4 style="margin-top: 0;">Important Information:</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>Please arrive at least 30 minutes before the show</li>
                        <li>Present this QR code at the entrance for entry</li>
                        <li>Cancellations allowed up to 24 hours before performance</li>
                        <li>No photography or recording during the performance</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated email. Please do not reply.</p>
                <p>For support, contact us at support@theatre.com or call (555) 123-4567</p>
                <p>&copy; 2025 Theatre Booking System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return email_html


def send_booking_confirmation(user_email: str, booking_data: dict, qr_code_base64: str) -> dict:
    """
    Send booking confirmation email to user
    
    In production, this would integrate with SendGrid, AWS SES, or similar email service
    For now, returns the email content that would be sent
    
    Business requirement: Send confirmation email with ticket details and QR code
    
    Args:
        user_email: Recipient email address
        booking_data: Dictionary with all booking information
        qr_code_base64: Base64 encoded QR code
    
    Returns:
        Dict with status and email content
    """
    email_html = format_booking_email(booking_data, qr_code_base64)
    
    # In production, send via email service:
    # import sendgrid
    # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    # message = Mail(
    #     from_email='noreply@theatre.com',
    #     to_emails=user_email,
    #     subject=f'Booking Confirmation - {booking_data["booking_reference"]}',
    #     html_content=email_html
    # )
    # response = sg.send(message)
    
    # For academic/demo purposes, return the email that would be sent
    return {
        "status": "success",
        "message": f"Confirmation email would be sent to {user_email}",
        "email_content": email_html,
        "recipient": user_email,
        "subject": f"Booking Confirmation - {booking_data.get('booking_reference', 'N/A')}"
    }


def check_booking_timeout(booking: any) -> bool:
    """
    Check if booking has exceeded 15-minute payment deadline
    
    Business requirement: Bookings must be paid within 15 minutes or released
    
    Args:
        booking: Booking model instance
    
    Returns:
        True if booking has timed out, False otherwise
    """
    if booking.booking_status != "Pending":
        return False
    
    if booking.payment_deadline is None:
        return False
    
    return datetime.utcnow() > booking.payment_deadline
