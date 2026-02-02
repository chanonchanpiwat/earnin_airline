import pytest
from fastapi.testclient import TestClient

from earnin_airline.app import create_application


client = TestClient(create_application())


def test_get_flights():
    response = client.get("/flights")

    assert response.status_code == 200
    assert response.json() == {
        "flights": [
            {
                "id": "AAA01",
                "departure_time": "2024-12-01T07:00:00+07:00",
                "arrival_time": "2024-12-01T09:00:00+07:00",
                "departure_airport": "DMK",
                "arrival_airport": "HYD",
            }
        ]
    }


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
        "expected_status": 200,
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
    return response.json()['passengers']


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
