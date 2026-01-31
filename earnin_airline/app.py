from datetime import datetime
from fastapi import FastAPI, HTTPException, APIRouter

from . import dto, timezone
from .passport import get_passport_detail
from .db import FlightRecord, get_db, EntityNotFound

router = APIRouter()


def create_application() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


db = get_db()


@router.get("/")
async def root():
    return {"service": "api", "healthy": True}


def parse_flight(flight: FlightRecord) -> dto.FlightResponse:
    departure_time, arrival_time = parse_timezone(
        flight.departure_time,
        flight.arrival_time,
        flight.departure_timezone,
        flight.arrival_timezone,
    )

    return dto.FlightResponse(
        id=flight.id,
        departure_time=departure_time,
        arrival_time=arrival_time,
        departure_airport=flight.departure_airport,
        arrival_airport=flight.arrival_airport,
    )


@router.get("/flights")
async def list_flight() -> dto.ListFlightsResponse:
    records = db.list_flights()
    return dto.ListFlightsResponse(flights=list(map(parse_flight, records)))


def parse_timezone(
    departure_time: datetime,
    arrival_time: datetime,
    departure_timezone: str,
    arrival_timezone: str,
) -> tuple[datetime, datetime]:
    if departure_timezone == arrival_timezone:
        return (
            timezone.apply_timezone(departure_time, "Asia/Bangkok"),
            timezone.apply_timezone(arrival_time, "Asia/Bangkok"),
        )

    return (
        timezone.apply_timezone(departure_time, "Europe/London"),
        timezone.apply_timezone(arrival_time, "Asia/Bangkok"),
    )


@router.get("/flights/{flight_id}/passengers")
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


@router.post("/flights/{flight_id}/passengers")
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


@router.put("/flights/{flight_id}/passengers/{customer_id}")
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


@router.delete("/flights/{flight_id}/passengers/{customer_id}")
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


app = create_application()
