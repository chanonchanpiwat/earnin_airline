from datetime import datetime
from zoneinfo import ZoneInfo


def apply_timezone(datetime_as_utc: datetime, zone_name: str):
    fixed_tz = datetime_as_utc.replace(tzinfo=ZoneInfo("UTC"))
    return fixed_tz.astimezone(ZoneInfo(zone_name))
