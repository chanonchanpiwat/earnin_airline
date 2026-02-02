import pytest
from tests.conftest import client
from tests.test_book_flight import assert_passenger_information
from tests.utils import assert_subset, get_passenger

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
    # book flight to create passenger
    response = client.post(f"/flights/{flight_id}/passengers", json=customer)
    assert response.status_code == 200, f"Error creating passenger: {response.text}"
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

    # update passenger information
    response = client.put(
        f"/flights/{flight_id}/passengers/{customer_id}",
        json=new_passenger,
    )

    assert response.status_code == expected_status, "Status code mismatch"
    assert_passenger_information(response.json(), expected_response)
    
    if expected_status == 200:
        # verify passenger is updated
        updated_passenger = get_passenger(flight_id, customer_id)

        # passenger updated should have correct information
        assert_subset(updated_passenger, expected_response, "Passenger")