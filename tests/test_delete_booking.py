import pytest
from tests.conftest import client
from tests.test_update_customer import create_passenger
from tests.utils import get_passenger

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
        "expected_response": None,
    },
]


@pytest.mark.parametrize("test_case", test_cases, ids=lambda tc: tc["name"])
def test_delete_passenger(test_case):
    flight_id, customer, expected_status, expected_response = (
        test_case["flight_id"],
        test_case["customer"],
        test_case["expected_status"],
        test_case["expected_response"],
    )
    passenger = create_passenger(flight_id, customer)
    customer_id = passenger["customer_id"]

    # delete booked passenger
    response = client.delete(f"/flights/{flight_id}/passengers/{customer_id}")

    assert response.status_code == expected_status
    assert response.json() == expected_response

    # verify passenger is deleted
    passenger = get_passenger(flight_id, customer_id)
    assert passenger is None, (
        f"Expected passenger to be deleted but got response: {passenger}"
    )
