from datetime import datetime
from earnin_airline import dto, timezone
from earnin_airline.db import FlightRecord


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
