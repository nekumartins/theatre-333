#!/usr/bin/env python3
"""
Test script for Theatre Booking System API
Tests all major endpoints to ensure the application is working correctly
"""
import requests
import json
from datetime import date, datetime

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}\n")

def test_health():
    """Test health check endpoint"""
    print_section("Testing Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_genres():
    """Test getting all genres"""
    print_section("Testing Get Genres")
    response = requests.get(f"{BASE_URL}/api/shows/genres/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Number of genres: {len(data)}")
    for genre in data[:3]:  # Show first 3
        print(f"  - {genre['genre_name']}: {genre['description']}")
    return response.status_code == 200

def test_get_shows():
    """Test getting all active shows"""
    print_section("Testing Get Shows")
    response = requests.get(f"{BASE_URL}/api/shows/?status=Active")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Number of shows: {len(data)}")
    for show in data:
        print(f"  - {show['title']} ({show['duration_minutes']} min)")
    return response.status_code == 200

def test_get_show_detail():
    """Test getting details of a specific show"""
    print_section("Testing Get Show Detail")
    response = requests.get(f"{BASE_URL}/api/shows/1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        show = response.json()
        print(f"Show: {show['title']}")
        print(f"Description: {show['description'][:80]}...")
        print(f"Duration: {show['duration_minutes']} minutes")
        print(f"Status: {show['show_status']}")
    return response.status_code == 200

def test_get_performances():
    """Test getting performances for a show"""
    print_section("Testing Get Performances")
    response = requests.get(f"{BASE_URL}/api/performances/show/1")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        performances = response.json()
        print(f"Number of performances: {len(performances)}")
        for perf in performances[:2]:  # Show first 2
            print(f"  - Date: {perf['performance_date']}, Time: {perf['start_time']}")
            print(f"    Available seats: {perf['available_seats']}/{perf['total_seats']}")
    return response.status_code == 200

def test_get_seats():
    """Test getting available seats for a performance"""
    print_section("Testing Get Available Seats")
    response = requests.get(f"{BASE_URL}/api/performances/1/seats")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        seats = data.get('seats', [])
        print(f"Total available seats: {len(seats)}")
        
        # Count by category
        categories = {}
        for seat in seats:
            cat = seat['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nSeats by category:")
        for cat, count in categories.items():
            print(f"  - {cat}: {count} seats")
        
        print(f"\nSample pricing (first seat in each category):")
        shown_cats = set()
        for seat in seats:
            cat = seat['category']
            if cat not in shown_cats:
                print(f"  - {cat}: £{seat['price']}")
                shown_cats.add(cat)
            if len(shown_cats) >= 4:
                break
    return response.status_code == 200

def test_user_registration():
    """Test user registration"""
    print_section("Testing User Registration")
    
    # Create a unique email for testing
    test_email = f"test_user_{datetime.now().timestamp()}@example.com"
    
    user_data = {
        "email": test_email,
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567899"
    }
    
    response = requests.post(f"{BASE_URL}/api/users/register", json=user_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"User created successfully!")
        print(f"  User ID: {data['user_id']}")
        print(f"  Message: {data['message']}")
        return True, data
    else:
        print(f"Registration failed: {response.text}")
        return False, None

def test_user_login():
    """Test user login with existing credentials"""
    print_section("Testing User Login")
    
    login_data = {
        "email": "john.doe@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/api/users/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Login successful!")
        print(f"  Token type: {data['token_type']}")
        print(f"  Token: {data['access_token'][:30]}...")
        return True, data['access_token']
    else:
        print(f"Login failed: {response.text}")
        return False, None

def test_create_booking(token):
    """Test creating a booking"""
    print_section("Testing Create Booking")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Decode token to get user_id (simple extraction from JWT)
    import base64
    import json
    # Decode the JWT payload (second part)
    payload_b64 = token.split('.')[1]
    # Add padding if needed
    payload_b64 += '=' * (4 - len(payload_b64) % 4)
    payload = json.loads(base64.b64decode(payload_b64))
    user_id = payload.get('user_id', 1)
    
    booking_data = {
        "user_id": user_id,
        "performance_id": 1,
        "seat_ids": [1, 2],  # Book 2 VIP seats
        "total_amount": 150.00
    }
    
    response = requests.post(
        f"{BASE_URL}/api/bookings/",
        json=booking_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        booking = response.json()
        print(f"Booking created successfully!")
        print(f"  Booking ID: {booking.get('booking_id', 'N/A')}")
        print(f"  Reference: {booking.get('booking_reference', 'N/A')}")
        print(f"  Total: £{booking.get('total_amount', 0)}")
        return True, booking.get('booking_id')
    else:
        print(f"Booking failed: {response.text}")
        return False, None

def test_get_user_bookings(token):
    """Test getting user's bookings"""
    print_section("Testing Get User Bookings")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Decode token to get user_id
    import base64
    import json
    payload_b64 = token.split('.')[1]
    payload_b64 += '=' * (4 - len(payload_b64) % 4)
    payload = json.loads(base64.b64decode(payload_b64))
    user_id = payload.get('user_id', 1)
    
    response = requests.get(f"{BASE_URL}/api/bookings/user/{user_id}", headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        bookings = response.json()
        print(f"Number of bookings: {len(bookings)}")
        for booking in bookings[:3]:  # Show first 3
            print(f"\n  Booking: {booking['booking_reference']}")
            print(f"  Date: {booking['booking_date']}")
            print(f"  Total: £{booking['total_amount']}")
            print(f"  Status: {booking['booking_status']}")
        return True
    else:
        print(f"Failed to get bookings: {response.text}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("THEATRE BOOKING SYSTEM API TESTS".center(60))
    print("="*60)
    
    results = {}
    
    # Basic endpoint tests
    results['Health Check'] = test_health()
    results['Get Genres'] = test_get_genres()
    results['Get Shows'] = test_get_shows()
    results['Get Show Detail'] = test_get_show_detail()
    results['Get Performances'] = test_get_performances()
    results['Get Available Seats'] = test_get_seats()
    
    # User authentication tests
    reg_success, reg_data = test_user_registration()
    results['User Registration'] = reg_success
    
    login_success, token = test_user_login()
    results['User Login'] = login_success
    
    # Booking tests (only if login succeeded)
    if login_success and token:
        booking_success, booking_id = test_create_booking(token)
        results['Create Booking'] = booking_success
        
        results['Get User Bookings'] = test_get_user_bookings(token)
    else:
        results['Create Booking'] = False
        results['Get User Bookings'] = False
    
    # Print summary
    print_section("TEST RESULTS SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {test_name}")
    
    print(f"\n{'─'*60}")
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print(f"{'─'*60}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to the API server.")
        print("Make sure the server is running on http://127.0.0.1:8000")
        exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
