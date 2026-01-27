from dataclasses import dataclass
from typing import Optional
import os

import aiohttp


PASSPORT_API_URL = os.getenv("PASSPORT_API", "http://localhost:8081")


@dataclass
class PassportDetail:
    passport_id: str
    first_name: str
    last_name: str


async def get_passport_detail(passport_id: str) -> Optional[PassportDetail]:
    async with aiohttp.ClientSession() as session:
        url = PASSPORT_API_URL + "/passport"
        body = {"passport_id": passport_id}
        async with session.get(url, json=body) as response:
            if response.status == 404:
                return None

            if response.status != 200:
                raise "Cannot connect to passport API: " + response.text()

            response_body = await response.json()
            return PassportDetail(
                passport_id=response_body["passport_id"],
                first_name=response_body["first_name"],
                last_name=response_body["last_name"],
            )
