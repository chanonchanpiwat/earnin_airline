from datetime import datetime
from zoneinfo import ZoneInfo

from tests.conftest import client
from tests.conftest import get_seed_data


def get_expected_flight_data():
    expected_flights = get_seed_data()
    for flight_data in expected_flights["flights"]:
        expected_departure_time, expected_arrival_time = parse_expected_flight_time(
            flight_data["departure_timezone"],
            flight_data["arrival_timezone"],
            flight_data["departure_time"],
            flight_data["arrival_time"],
        )

        # update flight data with adjusted timezones
        flight_data["departure_time"] = expected_departure_time
        flight_data["arrival_time"] = expected_arrival_time

    return expected_flights


def test_get_flights():
    expected_flights_data = get_expected_flight_data()

    # retrieve flights
    response = client.get("/flights")

    assert response.status_code == 200, "Failed to retrieve flights"
    assert_flights_information(response.json(), expected_flights_data)


def assert_flights_information(actual, expected):
    actual_flights, expected_flights = actual["flights"], expected["flights"]

    assert len(actual_flights) == len(expected_flights), "Number of flights mismatch"

    for actual_flight, expected_flight in zip(actual_flights, expected_flights):
        assert_flight(actual_flight, expected_flight)


def assert_flight(actual, expected):
    assert actual["departure_airport"] == expected["departure_airport"], (
        "Departure airport mismatch"
    )
    assert actual["arrival_airport"] == expected["arrival_airport"], (
        "Arrival airport mismatch"
    )
    assert (
        datetime.fromisoformat(actual["departure_time"]) == expected["departure_time"]
    ), "Departure time mismatch"
    assert datetime.fromisoformat(actual["arrival_time"]) == expected["arrival_time"], (
        "Arrival time mismatch"
    )


def parse_expected_flight_time(
    departure_timezone: str,
    arrival_timezone: str,
    utc_departure_time: datetime,
    utc_arrival_time: datetime,
):
    """
    given flight
    - same timezone for departure and arrival then both time will be converted to Asia/Bangkok timezone
    - different timezone for departure and arrival then departure time will be converted to Europe/London timezone and arrival time will be converted to Asia/Bangkok timezone
    """

    if departure_timezone == arrival_timezone:
        expected_departure_time = (
            datetime.fromisoformat(utc_departure_time)
            .replace(tzinfo=ZoneInfo("UTC"))
            .astimezone(ZoneInfo("Asia/Bangkok"))
        )

        expected_arrival_time = (
            datetime.fromisoformat(utc_arrival_time)
            .replace(tzinfo=ZoneInfo("UTC"))
            .astimezone(ZoneInfo("Asia/Bangkok"))
        )
    else:
        expected_departure_time = (
            datetime.fromisoformat(utc_departure_time)
            .replace(tzinfo=ZoneInfo("UTC"))
            .astimezone(ZoneInfo("Europe/London"))
        )

        expected_arrival_time = (
            datetime.fromisoformat(utc_arrival_time)
            .replace(tzinfo=ZoneInfo("UTC"))
            .astimezone(ZoneInfo("Asia/Bangkok"))
        )

    return expected_departure_time, expected_arrival_time
