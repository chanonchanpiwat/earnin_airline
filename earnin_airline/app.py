from fastapi import FastAPI, HTTPException

from . import dto, timezone
from .passport import get_passport_detail
from .db import get_db, EntityNotFound

app = FastAPI()
db = get_db()


@app.get("/")
async def root():
    return {"service": "api", "healthy": True}


@app.get("/flights")
async def list_flight() -> dto.ListFlightsResponse:
    records = db.list_flights()
    return dto.ListFlightsResponse(
        flights=[
            dto.FlightResponse(
                id=record.id,
                departure_time=timezone.apply_timezone(
                    record.departure_time, record.departure_timezone
                ),
                arrival_time=timezone.apply_timezone(
                    record.arrival_time, record.arrival_timezone
                ),
                departure_airport=record.departure_airport,
                arrival_airport=record.arrival_airport,
            )
            for record in records
        ],
    )


@app.get("/flights/{flight_id}/passengers")
async def list_passengers(flight_id: str):
    passengers = db.list_passengers(flight_id)
    return dto.ListPassengerResponse(
        passengers=[
            dto.PassengerResponse(
                flight_id=record.flight_id,
                customer_id=record.customer_id,
                passport_id=record.customer.passport_id,
                first_name=record.customer.first_name,
                last_name=record.customer.last_name,
            )
            for record in passengers
        ]
    )


@app.post("/flights/{flight_id}/passengers")
async def create_passenger(
    flight_id: str, create_req: dto.CreateOrUpdatePassengerRequest
) -> dto.PassengerResponse:
    validate_flight_id(flight_id)
    await validate_passport(create_req)

    result = db.create_passenger(
        flight_id=flight_id,
        passport_id=create_req.passport_id,
        first_name=create_req.first_name,
        last_name=create_req.last_name,
    )
    return dto.PassengerResponse(
        flight_id=result.flight_id,
        customer_id=result.customer.id,
        passport_id=result.customer.passport_id,
        first_name=result.customer.first_name,
        last_name=result.customer.last_name,
    )


@app.put("/flights/{flight_id}/passengers/{customer_id}")
async def update_passenger(
    flight_id: str, customer_id: int, update_req: dto.CreateOrUpdatePassengerRequest
) -> dto.PassengerResponse:
    validate_flight_id(flight_id)
    await validate_passport(update_req)

    try:
        result = db.update_passenger(
            flight_id=flight_id,
            customer_id=customer_id,
            passport_id=update_req.passport_id,
            first_name=update_req.first_name,
            last_name=update_req.last_name,
        )

        return dto.PassengerResponse(
            flight_id=result.flight_id,
            customer_id=result.customer.id,
            passport_id=result.customer.passport_id,
            first_name=result.customer.first_name,
            last_name=result.customer.last_name,
        )

    except EntityNotFound:
        raise HTTPException(
            status_code=404, detail=f"Passenger:{customer_id} not found."
        )


@app.delete("/flights/{flight_id}/passengers/{customer_id}")
async def delete_passenger(flight_id: str, customer_id: int):
    try:
        db.delete_passenger(flight_id, customer_id)
        return None
    except EntityNotFound:
        raise HTTPException(
            status_code=404, detail=f"Passenger:{customer_id} not found."
        )


async def validate_passport(req=dto.CreateOrUpdatePassengerRequest):
    detail = await get_passport_detail(req.passport_id)
    if not detail:
        raise HTTPException(status_code=400, detail="Passport not found.")

    is_detail_valid = (
        detail.first_name == req.first_name and detail.last_name == req.last_name
    )

    if not is_detail_valid:
        raise HTTPException(
            status_code=400, detail="Firstname or Lastname is mismatch."
        )


def validate_flight_id(flight_id: str):
    db = get_db()
    if not db.does_flight_exists(flight_id):
        raise HTTPException(status_code=404, detail=f"Flight:{flight_id} not found.")
