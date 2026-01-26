from datetime import datetime
from typing import List

from pydantic import BaseModel


class CreateOrUpdatePassengerRequest(BaseModel):
    passport_id: str
    first_name: str
    last_name: str


class PassengerResponse(BaseModel):
    flight_id: str
    customer_id: int
    passport_id: str
    first_name: str
    last_name: str


class ListPassengerResponse(BaseModel):
    passengers: List[PassengerResponse]


class FlightResponse(BaseModel):
    id: str
    departure_time: datetime
    arrival_time: datetime
    departure_airport: str
    arrival_airport: str


class ListFlightsResponse(BaseModel):
    flights: List[FlightResponse]
