from earnin_airline import dto
from .conftest import client


def get_passengers_by_flight(flight_id):
    response = client.get(f"/flights/{flight_id}/passengers")
    assert response.status_code == 200, (
        f"Error could not get passengers by flight {flight_id} error: {response.text}"
    )
    return response.json()["passengers"]


def get_passenger(flight_id: int, customer_id: int) -> dto.PassengerResponse:
    passengers = get_passengers_by_flight(flight_id)
    matched_passengers = [p for p in passengers if p["customer_id"] == customer_id]
    if len(matched_passengers) == 0:
        return None
    return matched_passengers[0]


def assert_subset(actual: dict, expected: dict, entity_name: str):
    for key, value in expected.items():
        assert actual[key] == value, (
            f"Expected {entity_name} field {key} to be {value}, but got {actual[key]}"
        )
