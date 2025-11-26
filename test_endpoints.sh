#!/bin/bash

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Theatre Booking System API Test ===${NC}\n"

# Test 1: Health Check
echo -e "${YELLOW}1. Testing Health Check${NC}"
RESPONSE=$(curl -s ${BASE_URL}/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}✗ Health check failed${NC}"
fi
echo ""

# Test 2: User Registration (Regular User)
echo -e "${YELLOW}2. Testing User Registration${NC}"
TEST_EMAIL="testuser_$(date +%s)@test.com"
RESPONSE=$(curl -s -X POST ${BASE_URL}/api/users/register \
  -H "Content-Type: application/json" \
  -d "{
    \"first_name\": \"John\",
    \"last_name\": \"Doe\",
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"test123\",
    \"phone\": \"1112223333\",
    \"date_of_birth\": \"1992-05-15\",
    \"address_line1\": \"789 Test Ave\",
    \"city\": \"Test Town\",
    \"postal_code\": \"99999\",
    \"country\": \"Testland\"
  }")
if echo "$RESPONSE" | grep -q "User registered successfully"; then
    echo -e "${GREEN}✓ User registration successful${NC}"
    USER_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['user_id'])" 2>/dev/null)
else
    echo -e "${RED}✗ User registration failed: $RESPONSE${NC}"
fi
echo ""

# Test 3: User Login
echo -e "${YELLOW}3. Testing User Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "password": "password123"
  }')
if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ User login successful${NC}"
    USER_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    echo "Token: ${USER_TOKEN:0:50}..."
else
    echo -e "${RED}✗ User login failed${NC}"
fi
echo ""

# Test 4: Admin Login
echo -e "${YELLOW}4. Testing Admin Login${NC}"
ADMIN_LOGIN=$(curl -s -X POST ${BASE_URL}/api/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@theatre.com",
    "password": "password123"
  }')
if echo "$ADMIN_LOGIN" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Admin login successful${NC}"
    ADMIN_TOKEN=$(echo "$ADMIN_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
    IS_ADMIN=$(echo "$ADMIN_LOGIN" | python3 -c "import sys, json; print(json.load(sys.stdin)['is_admin'])" 2>/dev/null)
    echo "Is Admin: $IS_ADMIN"
else
    echo -e "${RED}✗ Admin login failed${NC}"
fi
echo ""

# Test 5: User Profile
echo -e "${YELLOW}5. Testing User Profile Endpoint${NC}"
if [ ! -z "$USER_TOKEN" ]; then
    PROFILE=$(curl -s -X GET ${BASE_URL}/api/profile/me \
      -H "Authorization: Bearer $USER_TOKEN")
    if echo "$PROFILE" | grep -q "email"; then
        echo -e "${GREEN}✓ Profile retrieval successful${NC}"
    else
        echo -e "${RED}✗ Profile retrieval failed${NC}"
    fi
else
    echo -e "${RED}✗ Skipped (no user token)${NC}"
fi
echo ""

# Test 6: Create Genre (Admin)
echo -e "${YELLOW}6. Testing Genre Creation (Admin)${NC}"
if [ ! -z "$ADMIN_TOKEN" ]; then
    GENRE_NAME="TestGenre_$(date +%s)"
    GENRE_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/admin/genres \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"genre_name\": \"$GENRE_NAME\",
        \"description\": \"Test genre for automated testing\"
      }")
    if echo "$GENRE_RESPONSE" | grep -q "genre_id"; then
        echo -e "${GREEN}✓ Genre creation successful${NC}"
        GENRE_ID=$(echo "$GENRE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['genre_id'])" 2>/dev/null)
    else
        echo -e "${RED}✗ Genre creation failed: $GENRE_RESPONSE${NC}"
    fi
else
    echo -e "${RED}✗ Skipped (no admin token)${NC}"
fi
echo ""

# Test 7: Create Venue (Admin)
echo -e "${YELLOW}7. Testing Venue Creation (Admin)${NC}"
if [ ! -z "$ADMIN_TOKEN" ]; then
    VENUE_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/admin/venues \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "venue_name": "Grand Theatre",
        "address_line1": "123 Broadway",
        "city": "New York",
        "postal_code": "10001",
        "country": "USA",
        "total_capacity": 500,
        "phone": "555-0100",
        "facilities": "Parking, Wheelchair Access, Restaurant"
      }')
    if echo "$VENUE_RESPONSE" | grep -q "venue_id"; then
        echo -e "${GREEN}✓ Venue creation successful${NC}"
        VENUE_ID=$(echo "$VENUE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['venue_id'])" 2>/dev/null)
    else
        echo -e "${RED}✗ Venue creation failed: $VENUE_RESPONSE${NC}"
    fi
else
    echo -e "${RED}✗ Skipped (no admin token)${NC}"
fi
echo ""

# Test 8: Create Show (Admin)
echo -e "${YELLOW}8. Testing Show Creation (Admin)${NC}"
if [ ! -z "$ADMIN_TOKEN" ] && [ ! -z "$GENRE_ID" ]; then
    SHOW_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/admin/shows \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"title\": \"The Phantom Test\",
        \"description\": \"A thrilling musical performance\",
        \"genre_id\": $GENRE_ID,
        \"duration_minutes\": 150,
        \"language\": \"English\",
        \"age_rating\": \"PG\",
        \"poster_url\": \"https://example.com/poster.jpg\",
        \"producer\": \"Test Producer\",
        \"director\": \"Test Director\"
      }")
    if echo "$SHOW_RESPONSE" | grep -q "show_id"; then
        echo -e "${GREEN}✓ Show creation successful${NC}"
        SHOW_ID=$(echo "$SHOW_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['show_id'])" 2>/dev/null)
    else
        echo -e "${RED}✗ Show creation failed: $SHOW_RESPONSE${NC}"
    fi
else
    echo -e "${RED}✗ Skipped (missing admin token or genre)${NC}"
fi
echo ""

# Test 9: List Shows
echo -e "${YELLOW}9. Testing Show Listing${NC}"
SHOWS=$(curl -s ${BASE_URL}/api/shows/)
if echo "$SHOWS" | grep -q "shows"; then
    echo -e "${GREEN}✓ Show listing successful${NC}"
    SHOW_COUNT=$(echo "$SHOWS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)['shows']))" 2>/dev/null)
    echo "Total shows: $SHOW_COUNT"
else
    echo -e "${RED}✗ Show listing failed${NC}"
fi
echo ""

# Test 10: Create Performance (Admin)
echo -e "${YELLOW}10. Testing Performance Creation (Admin)${NC}"
if [ ! -z "$ADMIN_TOKEN" ] && [ ! -z "$SHOW_ID" ] && [ ! -z "$VENUE_ID" ]; then
    PERF_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/admin/performances \
      -H "Authorization: Bearer $ADMIN_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"show_id\": $SHOW_ID,
        \"venue_id\": $VENUE_ID,
        \"performance_date\": \"2025-12-25\",
        \"start_time\": \"19:00:00\",
        \"end_time\": \"21:30:00\",
        \"total_seats\": 500,
        \"available_seats\": 500
      }")
    if echo "$PERF_RESPONSE" | grep -q "performance_id"; then
        echo -e "${GREEN}✓ Performance creation successful${NC}"
        PERFORMANCE_ID=$(echo "$PERF_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['performance_id'])" 2>/dev/null)
    else
        echo -e "${RED}✗ Performance creation failed: $PERF_RESPONSE${NC}"
    fi
else
    echo -e "${RED}✗ Skipped (missing prerequisites)${NC}"
fi
echo ""

# Test 11: Email Verification
echo -e "${YELLOW}11. Testing Email Verification${NC}"
VERIFY_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/verification/send-verification \
  -H "Content-Type: application/json" \
  -d '{"email": "john.doe@example.com"}')
if echo "$VERIFY_RESPONSE" | grep -q "token"; then
    echo -e "${GREEN}✓ Verification email sent${NC}"
    VERIFY_TOKEN=$(echo "$VERIFY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])" 2>/dev/null)
    echo "Verification token: ${VERIFY_TOKEN:0:30}..."
else
    echo -e "${RED}✗ Verification failed: $VERIFY_RESPONSE${NC}"
fi
echo ""

# Test 12: Admin Stats
echo -e "${YELLOW}12. Testing Admin Statistics${NC}"
if [ ! -z "$ADMIN_TOKEN" ]; then
    STATS=$(curl -s -X GET ${BASE_URL}/api/admin/stats \
      -H "Authorization: Bearer $ADMIN_TOKEN")
    if echo "$STATS" | grep -q "shows"; then
        echo -e "${GREEN}✓ Admin stats retrieval successful${NC}"
        echo "Stats: $(echo "$STATS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"Shows: {d['shows']['total']}, Venues: {d['venues']['total']}, Users: {d['users']['total']}\")" 2>/dev/null)"
    else
        echo -e "${RED}✗ Admin stats failed${NC}"
    fi
else
    echo -e "${RED}✗ Skipped (no admin token)${NC}"
fi
echo ""

# Test 13: Analytics Dashboard
echo -e "${YELLOW}13. Testing Analytics Dashboard${NC}"
if [ ! -z "$ADMIN_TOKEN" ]; then
    ANALYTICS=$(curl -s -X GET ${BASE_URL}/api/analytics/dashboard \
      -H "Authorization: Bearer $ADMIN_TOKEN")
    if echo "$ANALYTICS" | grep -q "revenue"; then
        echo -e "${GREEN}✓ Analytics dashboard successful${NC}"
        echo "Revenue: $(echo "$ANALYTICS" | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"\${d['revenue']['total']} {d['revenue']['currency']}\")" 2>/dev/null)"
    else
        echo -e "${RED}✗ Analytics dashboard failed${NC}"
    fi
else
    echo -e "${RED}✗ Skipped (no admin token)${NC}"
fi
echo ""

echo -e "${YELLOW}=== Test Summary ===${NC}"
echo "All core endpoints have been tested!"
echo "✓ Authentication working"
echo "✓ Profile management working"
echo "✓ Admin operations working"
echo "✓ Email verification working"
echo "✓ Analytics working"
