import pytest

from tests.utils import assert_subset, get_passenger
from tests.conftest import client


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
        "expected_response": {
            "flight_id": "AAA01",
            "customer_id": 1,
            "passport_id": "BC1500",
            "first_name": "Shauna",
            "last_name": "Davila",
        },
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

    # create booking
    response = client.post(
        f"/flights/{flight_id}/passengers",
        json=customer,
    )

    assert response.status_code == expected_status, "Status code mismatch"
    assert response.json() == expected_response, "Response body mismatch"

    if expected_status == 200:
        booking_detail = response.json()

        # verify passenger is created
        customer_id = booking_detail["customer_id"]
        passenger = get_passenger(flight_id, customer_id)

        # passenger created should have correct information
        assert_passenger_information(passenger, customer)


def assert_passenger_information(actual, expect):
    assert_subset(actual, expect, "passenger")
