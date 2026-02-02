import os
from pathlib import Path
import psycopg2
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
import yaml
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="[%(asctime)s] %(levelname)s %(name)s — %(message)s",
)

logger = logging.getLogger("test")

BASE_DIR = Path(__file__).parent.parent
SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"
SEED_PATH = BASE_DIR / "db" / "seeds.yml"

def get_seed_data():
    return yaml.safe_load(SEED_PATH.read_text())


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


def get_connection():
    return psycopg2.connect(**TestDBConfig.get_connection_params())


def seed_data():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for f in yaml.safe_load(SEED_PATH.read_text()).get("flights", []):
                    cur.execute(
                        """
                        INSERT INTO flights
                        (id, departure_time, arrival_time,
                         departure_airport, arrival_airport,
                         departure_timezone, arrival_timezone)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        (
                            f["id"],
                            f["departure_time"],
                            f["arrival_time"],
                            f["departure_airport"],
                            f["arrival_airport"],
                            f["departure_timezone"],
                            f["arrival_timezone"],
                        ),
                    )

            conn.commit()

    except Exception as e:
        logger.error(f"[SEED ERROR] Failed inserting seed data: {e}")
        raise


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    postgres.start()

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)

    init_schema()
    seed_data()


def init_schema():
    sql = SCHEMA_PATH.read_text()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()

    except Exception as e:
        logger.error(f"[SCHEMA ERROR] Failed executing schema SQL error: {e}")
        raise


@pytest.fixture(scope="function", autouse=True)
def clean_up():
    clear_up_passenger()


def clear_up_passenger():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE customers, passengers;")
            conn.commit()
