from fastapi import FastAPI, HTTPException, Header, Query
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="TBO Mock Travel Platform", version="2.4.0")

# In-memory mock database
AGENCIES = {
    "AGENCY-001": {"name": "Apex Voyages", "credit": 50000},
    "AGENCY-002": {"name": "BlueSky Travels", "credit": 12000},
}

BOOKINGS = {
    "BK-1001": {
        "booking_id": "BK-1001",
        "agency_id": "AGENCY-001",
        "passenger_name": "John Doe",
        "passport_no": "Z8912345",
        "flight": "AI-202 (DEL -> LHR)",
        "price": 1200,
        "status": "CONFIRMED"
    },
    "BK-1002": {
        "booking_id": "BK-1002",
        "agency_id": "AGENCY-002",
        "passenger_name": "Jane Smith",
        "passport_no": "A4421998",
        "flight": "EK-505 (BOM -> DXB)",
        "price": 850,
        "status": "CONFIRMED"
    }
}

class BookingRequest(BaseModel):
    agency_id: str
    flight_number: str
    passenger_name: str
    passport_no: str
    price: float  # VULNERABLE: Client can override price!

class RefundRequest(BaseModel):
    booking_id: str
    amount: float

# ----------------- ACTIVE ENDPOINTS -----------------

@app.get("/api/v2/flights/search")
def search_flights(origin: str = "DEL", destination: str = "DXB"):
    return {
        "status": "success",
        "results": [
            {"flight": "AI-202", "origin": origin, "destination": destination, "price": 450.0},
            {"flight": "EK-505", "origin": origin, "destination": destination, "price": 520.0}
        ]
    }

# VULNERABILITY 1: Business Logic - Price Tampering
# Bug: The endpoint trusts the 'price' supplied in the request body instead of calculating it server-side.
@app.post("/api/v2/bookings/create")
def create_booking(req: BookingRequest):
    new_id = f"BK-{len(BOOKINGS) + 1001}"
    BOOKINGS[new_id] = {
        "booking_id": new_id,
        "agency_id": req.agency_id,
        "passenger_name": req.passenger_name,
        "passport_no": req.passport_no,
        "flight": req.flight_number,
        "price": req.price,  # Accepts whatever client sends, even price=0 or price=1
        "status": "CONFIRMED"
    }
    return {
        "status": "success",
        "message": "Booking created",
        "booking": BOOKINGS[new_id]
    }

# VULNERABILITY 2: IDOR (Insecure Direct Object Reference) + PII Leak
# Bug: Any authenticated or unauthenticated agency can fetch ANY booking_id and view passport/credit data.
@app.get("/api/v2/bookings/{booking_id}")
def get_booking(booking_id: str, x_agency_id: Optional[str] = Header(None)):
    if booking_id not in BOOKINGS:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Notice: NO cross-tenant agency check! Even if x_agency_id is AGENCY-002, they can see AGENCY-001's booking!
    return {
        "status": "success",
        "booking": BOOKINGS[booking_id]
    }

# VULNERABILITY 3: Double Refund / Logic Abuse
@app.post("/api/v2/refunds/request")
def process_refund(req: RefundRequest):
    if req.booking_id not in BOOKINGS:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking = BOOKINGS[req.booking_id]
    # Bug: Doesn't check if already refunded, allows infinite refund loops
    return {
        "status": "success",
        "refund_id": "RF-9988",
        "amount_refunded": req.amount,
        "booking_status": "REFUNDED"
    }

# ----------------- ZOMBIE ENDPOINT -----------------
# VULNERABILITY 4: Zombie API (/v1 route abandoned but alive, no auth, gives secret 50% discount code)
@app.get("/api/v1/legacy/discounts")
def get_legacy_discounts():
    return {
        "warning": "DEPRECATED ENDPOINT",
        "promo_code": "SECRET_STAFF_50_OFF",
        "discount_percent": 50,
        "expires": "2021-12-31"  # Still accepted by backend!
    }

# ----------------- SHADOW ENDPOINT -----------------
# VULNERABILITY 5: Shadow API (Undocumented internal debugging endpoint exposed to public)
@app.get("/api/v2/internal/admin/stats")
def internal_admin_stats():
    return {
        "service": "tbo-booking-engine",
        "environment": "production-like-staging",
        "active_agencies": len(AGENCIES),
        "total_revenue": sum(b["price"] for b in BOOKINGS.values()),
        "db_connection": "sqlite:///tbo_travel.db"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
