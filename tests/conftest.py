import os
import psycopg2
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy


class TestDBConfig:
    HOST = os.getenv("DB_HOST", "localhost")
    PORT = os.getenv("DB_PORT", "5432")
    USERNAME = os.getenv("DB_USERNAME", "postgres")
    PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DATABASE = os.getenv("DB_NAME", "airline")

    @classmethod
    def get_connection_params(cls):
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "user": cls.USERNAME,
            "password": cls.PASSWORD,
            "dbname": cls.DATABASE,
        }


def get_connection():
    return psycopg2.connect(**TestDBConfig.get_connection_params())


def init_db():
    schemas = [
        """CREATE TABLE IF NOT EXISTS flights (
            id                 VARCHAR(8)  PRIMARY KEY,
            departure_time     TIMESTAMP   NOT NULL,
            arrival_time       TIMESTAMP   NOT NULL,
            departure_airport  VARCHAR(3)  NOT NULL,
            arrival_airport    VARCHAR(3)  NOT NULL,
            departure_timezone VARCHAR(30) NOT NULL,
            arrival_timezone   VARCHAR(30) NOT NULL
        );""",
        """CREATE TABLE IF NOT EXISTS customers (
            id          SERIAL       PRIMARY KEY,
            passport_id VARCHAR(20)  NOT NULL UNIQUE,
            first_name  VARCHAR(50)  NOT NULL,
            last_name   VARCHAR(50)  NOT NULL
        );""",
        """
        CREATE UNIQUE INDEX IF NOT EXISTS customers__passport_id_idx
            ON customers (passport_id);
        """,
        """CREATE TABLE IF NOT EXISTS passengers (
            flight_id   VARCHAR(8) NOT NULL REFERENCES flights(id) ON DELETE CASCADE,
            customer_id INT        NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
            PRIMARY KEY (flight_id, customer_id)
        );""",
    ]

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for statement in schemas:
                    cur.execute(statement)

                seed_flight = (
                    "AAA01",
                    "2024-12-01 00:00:00",
                    "2024-12-01 02:00:00",
                    "DMK",
                    "HYD",
                    "Asia/Bangkok",
                    "Asia/Bangkok",
                )

                cur.execute(
                    """
                    INSERT INTO flights (id, departure_time, arrival_time, departure_airport, 
                                         arrival_airport, departure_timezone, arrival_timezone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING;
                """,
                    seed_flight,
                )

            conn.commit()
    except Exception as e:
        print(f"Unable to initialize Test Database initialize error: {e}")


def clear_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE customers, passengers;")
            conn.commit()


postgres = PostgresContainer(
    "postgres:16-alpine",
    username=TestDBConfig.USERNAME,
    password=TestDBConfig.PASSWORD,
    dbname=TestDBConfig.DATABASE,
).waiting_for(
    LogMessageWaitStrategy(
        "database system is ready to accept connections"
    ).with_startup_timeout(30)
)


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    postgres.start()

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)

    init_db()


@pytest.fixture(scope="function", autouse=True)
def setup_data():
    clear_db()
