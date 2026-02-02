from zoneinfo import ZoneInfo
import pytest
from fastapi.testclient import TestClient

from earnin_airline.app import create_application
from tests.conftest import get_seed_data

from datetime import datetime

client = TestClient(create_application())


def assert_flight(actual, raw_data):
    expected_departure_time, expected_arrival_time = parse_expected_flight_time(
        raw_data
    )

    assert actual["id"] == raw_data["id"]
    assert actual["departure_airport"] == raw_data["departure_airport"]
    assert actual["arrival_airport"] == raw_data["arrival_airport"]
    assert datetime.fromisoformat(actual["departure_time"]) == expected_departure_time
    assert datetime.fromisoformat(actual["arrival_time"]) == expected_arrival_time


def parse_expected_flight_time(flight_data):
    """
    given flight
    - same timezone for departure and arrival then both time will be converted to Asia/Bangkok timezone
    - different timezone for departure and arrival then departure time will be converted to Europe/London timezone and arrival time will be converted to Asia/Bangkok timezone
    """
    departure_timezone, arrival_timezone, raw_departure_time, raw_arrival_time = (
        flight_data["departure_timezone"],
        flight_data["arrival_timezone"],
        flight_data["departure_time"],
        flight_data["arrival_time"],
    )

    if departure_timezone == arrival_timezone:
        expected_departure_time = (
            datetime.fromisoformat(raw_departure_time)
            .replace(tzinfo=ZoneInfo("UTC"))
            .astimezone(ZoneInfo("Asia/Bangkok"))
        )

        expected_arrival_time = (
            datetime.fromisoformat(raw_arrival_time)
            .replace(tzinfo=ZoneInfo("UTC"))
            .astimezone(ZoneInfo("Asia/Bangkok"))
        )
    else:
        expected_departure_time = (
            datetime.fromisoformat(raw_departure_time)
            .replace(tzinfo=ZoneInfo("UTC"))
            .astimezone(ZoneInfo("Europe/London"))
        )

        expected_arrival_time = (
            datetime.fromisoformat(raw_arrival_time)
            .replace(tzinfo=ZoneInfo("UTC"))
            .astimezone(ZoneInfo("Asia/Bangkok"))
        )

    return expected_departure_time, expected_arrival_time


def assert_flights(actual, raw_data):
    assert len(actual["flights"]) == len(raw_data["flights"])
    for actual_flight, raw_flight_data in zip(actual["flights"], raw_data["flights"]):
        assert_flight(actual_flight, raw_flight_data)


def test_get_flights():
    seed_flights_data = get_seed_data()

    response = client.get("/flights")

    assert response.status_code == 200
    assert_flights(response.json(), seed_flights_data)


test_cases = [
    {
        "name": "given customer with valid passport, should be able to create passenger",
        "customer": {
            "passport_id": "BC1500",
            "first_name": "Shauna",
            "last_name": "Davila",
        },
        "flight_id": "AAA01",
        "expected_status": 200,
        "expected_response": {"passport_id": "BC1500", "flight_id": "AAA01"},
    },
    {
        "name": "given customer with missing first_name, should not be able to create passenger",
        "customer": {
            "passport_id": "BC1500",
            "first_name": "Invalid_Name",
            "last_name": "Davila",
        },
        "flight_id": "AAA01",
        "expected_status": 400,
        "expected_response": {"detail": "Firstname or Lastname is mismatch."},
    },
    {
        "name": "given customer with missing last_name, should not be able to create passenger",
        "customer": {
            "passport_id": "BC1500",
            "first_name": "Shauna",
            "last_name": "Invalid_last_name",
        },
        "flight_id": "AAA01",
        "expected_status": 400,
        "expected_response": {"detail": "Firstname or Lastname is mismatch."},
    },
    {
        "name": "given customer with invalid passport, should not be able to create passenger",
        "customer": {
            "passport_id": "XY9999",
            "first_name": "John",
            "last_name": "Dean",
        },
        "flight_id": "AAA01",
        "expected_status": 400,
        "expected_response": {"detail": "Passport not found."},
    },
]


def assert_passenger(actual, expect):
    for key, value in expect.items():
        assert actual[key] == value, (
            f"expected {key} to be {value}, but got {actual[key]}"
        )


@pytest.mark.parametrize(
    "test_case", test_cases, ids=lambda test_case: test_case["name"]
)
def test_create_passenger(test_case):
    flight_id, customer, expected_status, expected_response = (
        test_case["flight_id"],
        test_case["customer"],
        test_case["expected_status"],
        test_case["expected_response"],
    )

    response = client.post(
        f"/flights/{flight_id}/passengers",
        json=customer,
    )

    assert response.status_code == expected_status
    assert_passenger(response.json(), expected_response)


test_cases = [
    {
        "name": "given valid customer and flight, should be able to update passenger",
        "flight": "AAA01",
        "customer": {
            "passport_id": "BC1500",
            "first_name": "Shauna",
            "last_name": "Davila",
        },
        "new_passenger": {
            "passport_id": "BC1501",
            "first_name": "admin",
            "last_name": "admin",
        },
        "expected_status": 200,
        "expected_response": {
            "first_name": "admin",
            "last_name": "admin",
            "passport_id": "BC1501",
        },
    },
    {
        "name": "given customer with invalid passport, should not be able to update passenger",
        "flight": "AAA01",
        "customer": {
            "passport_id": "BC1500",
            "first_name": "Shauna",
            "last_name": "Davila",
        },
        "new_passenger": {
            "passport_id": "invalid_BC1501",
            "first_name": "admin",
            "last_name": "admin",
        },
        "expected_status": 400,
        "expected_response": {"detail": "Passport not found."},
    },
]


def create_passenger(flight_id, customer):
    response = client.post(f"/flights/{flight_id}/passengers", json=customer)
    assert response.status_code == 200, "Setup failed: Could not create passenger"
    return response.json()


@pytest.mark.parametrize("test_case", test_cases, ids=lambda tc: tc["name"])
def test_update_passenger(test_case):
    flight_id, customer, new_passenger, expected_status, expected_response = (
        test_case["flight"],
        test_case["customer"],
        test_case["new_passenger"],
        test_case["expected_status"],
        test_case["expected_response"],
    )
    passenger = create_passenger(flight_id, customer)
    customer_id = passenger["customer_id"]

    response = client.put(
        f"/flights/{flight_id}/passengers/{customer_id}",
        json=new_passenger,
    )

    assert response.status_code == expected_status
    assert_passenger(response.json(), expected_response)


test_cases = [
    {
        "name": "given valid customer and flight, should be able to delete passenger",
        "flight_id": "AAA01",
        "customer": {
            "passport_id": "BC1500",
            "first_name": "Shauna",
            "last_name": "Davila",
        },
        "expected_status": 200,
    },
]


def get_passengers_by_flight(flight_id):
    response = client.get(f"/flights/{flight_id}/passengers")
    assert response.status_code == 200, (
        "Setup failed: Could not get passengers by flight"
    )
    return response.json()["passengers"]


@pytest.mark.parametrize("test_case", test_cases, ids=lambda tc: tc["name"])
def test_delete_passenger(test_case):
    flight_id, customer, expected_status = (
        test_case["flight_id"],
        test_case["customer"],
        test_case["expected_status"],
    )
    passenger = create_passenger(flight_id, customer)
    customer_id = passenger["customer_id"]

    response = client.delete(f"/flights/{flight_id}/passengers/{customer_id}")

    assert response.status_code == expected_status
    for passenger in get_passengers_by_flight(flight_id):
        assert not (passenger["customer_id"] == customer_id), (
            f"expected customer: {customer_id} to be deleted"
        )
