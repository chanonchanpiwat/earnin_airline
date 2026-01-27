from datetime import datetime
from typing import Iterable
import os

from sqlalchemy import create_engine, select, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


Base = declarative_base()


class FlightRecord(Base):
    __tablename__ = "flights"

    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    departure_time: Mapped[datetime] = mapped_column(DateTime)
    arrival_time: Mapped[datetime] = mapped_column(DateTime)
    departure_airport: Mapped[str] = mapped_column(String(3))
    arrival_airport: Mapped[str] = mapped_column(String(3))
    departure_timezone: Mapped[str] = mapped_column(String(30))
    arrival_timezone: Mapped[str] = mapped_column(String(30))


class CustomerRecord(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    passport_id: Mapped[str] = mapped_column(String(20), unique=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))


class PassengerRecord(Base):
    __tablename__ = "passengers"

    flight_id: Mapped[str] = mapped_column(ForeignKey("flights.id"), primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), primary_key=True
    )

    flight: Mapped["FlightRecord"] = relationship()
    customer: Mapped["CustomerRecord"] = relationship()


SQLALCHEMY_DATABASE_URL = (
    os.getenv("DATABASE_URL") or "postgresql://postgres:postgres@localhost/airline"
)


class EntityNotFound(Exception):
    pass


class DB:
    def __init__(self) -> None:
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL)
        self.session = sessionmaker(
            self.engine,
            expire_on_commit=False,
        )

    def list_flights(self) -> Iterable[FlightRecord]:
        with self.session() as session:
            stmt = select(FlightRecord)
            return list(session.scalars(stmt))

    def does_flight_exists(self, flight_id: str) -> bool:
        with self.session() as session:
            stmt = select(exists().where(FlightRecord.id == flight_id))
            does_exists = next(session.scalars(stmt))
            return does_exists

    def list_passengers(self, flight_id: str) -> Iterable[PassengerRecord]:
        with self.session() as session:
            stmt = (
                select(PassengerRecord)
                .options(joinedload(PassengerRecord.customer))
                .where(PassengerRecord.flight_id == flight_id)
            )

            return list(session.scalars(stmt))

    def create_passenger(
        self, flight_id: str, passport_id: str, first_name: str, last_name: str
    ) -> PassengerRecord:
        with self.session() as session:
            fetch_customer_stmt = select(CustomerRecord).where(
                CustomerRecord.passport_id == passport_id
            )
            customers = session.scalars(fetch_customer_stmt)
            customer = next(customers, None)
            if not customer:
                customer = CustomerRecord(
                    passport_id=passport_id, first_name=first_name, last_name=last_name
                )
                session.add(customer)

            passenger = PassengerRecord(flight_id=flight_id, customer=customer)
            session.add(passenger)
            session.commit()

            return passenger

    def update_passenger(
        self,
        flight_id: str,
        customer_id: int,
        passport_id: str,
        first_name: str,
        last_name: str,
    ) -> PassengerRecord:
        with self.session() as session:
            fetch_passenger_stmt = select(PassengerRecord).where(
                PassengerRecord.flight_id == flight_id
                and PassengerRecord.customer_id == customer_id
            )
            passenger = next(session.scalars(fetch_passenger_stmt), None)
            if not passenger:
                raise EntityNotFound()

            customer = passenger.customer
            customer.passport_id = passport_id
            customer.first_name = first_name
            customer.last_name = last_name
            session.commit()

            return passenger

    def delete_passenger(self, flight_id: str, customer_id: int) -> PassengerRecord:
        with self.session() as session:
            fetch_passenger_stmt = select(PassengerRecord).where(
                PassengerRecord.flight_id == flight_id
                and PassengerRecord.customer_id == customer_id
            )

            passenger = next(session.scalars(fetch_passenger_stmt), None)
            if not passenger:
                raise EntityNotFound()

            session.delete(passenger)
            session.commit()

            return passenger


db = None


def get_db() -> DB:
    global db
    if not db:
        db = DB()

    return db
