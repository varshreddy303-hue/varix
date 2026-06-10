from datetime import datetime
import math
from typing import Any, Dict, Optional

from ..models import TripPackage


def _safe_float(value: Optional[float], default: float = 0.0) -> float:
    return float(value) if value is not None else default


def _calculate_distance(start_km: int, end_km: Optional[int]) -> Optional[float]:
    if end_km is None:
        return None
    return float(end_km - start_km)


def _normalize_datetime_pair(start_time: datetime, end_time: datetime) -> tuple[datetime, datetime]:
    if start_time.tzinfo is None and end_time.tzinfo is not None:
        start_time = start_time.replace(tzinfo=end_time.tzinfo)
    elif end_time.tzinfo is None and start_time.tzinfo is not None:
        end_time = end_time.replace(tzinfo=start_time.tzinfo)
    return start_time, end_time


def _calculate_hours_used(start_time: Optional[datetime], end_time: Optional[datetime]) -> Optional[float]:
    if not start_time or not end_time:
        return None
    start_time, end_time = _normalize_datetime_pair(start_time, end_time)
    if end_time < start_time:
        return None
    duration_hours = (end_time - start_time).total_seconds() / 3600.0
    return float(math.ceil(duration_hours)) if duration_hours > 0 else 0.0


def _calculate_days_used(start_time: Optional[datetime], end_time: Optional[datetime]) -> Optional[int]:
    if not start_time or not end_time:
        return None
    start_time, end_time = _normalize_datetime_pair(start_time, end_time)
    days = (end_time.date() - start_time.date()).days + 1
    return max(1, days)


def _normalize_category(category: Optional[str]) -> str:
    return category.strip().lower() if category else ""


def calculate_trip_financials(package: Optional[TripPackage], values: Dict[str, Any]) -> Dict[str, Any]:
    start_km = values.get("start_km")
    end_km = values.get("end_km")
    start_time = values.get("start_time")
    end_time = values.get("end_time")

    distance_km = _calculate_distance(start_km, end_km) if start_km is not None else None
    trip_date = start_time.date() if isinstance(start_time, datetime) else None
    included_km = None
    included_hours = None
    hours_used = None
    days_used = None
    extra_km = None
    extra_hours = None
    extra_km_amount = None
    extra_hour_amount = None
    package_amount = None

    driver_bata = _safe_float(values.get("driver_bata"))
    night_charges = _safe_float(values.get("night_charges"))
    permit_amount = _safe_float(values.get("permit_amount"))
    state_tax_amount = _safe_float(values.get("state_tax_amount"))
    toll_amount = _safe_float(values.get("toll_amount"))
    parking_amount = _safe_float(values.get("parking_amount"))

    package_amount = _safe_float(values.get("package_amount")) if values.get("package_amount") is not None else 0.0
    extra_km_rate = _safe_float(values.get("extra_km_rate"))
    extra_hour_rate = _safe_float(values.get("extra_hour_rate"))
    minimum_km_per_day = values.get("minimum_km_per_day")
    km_rate = _safe_float(values.get("km_rate"))

    if package:
        category = _normalize_category(package.package_category)
        package_amount = float(package.base_amount) if package.base_amount is not None else package_amount
        extra_km_rate = extra_km_rate or _safe_float(package.extra_km_rate)
        extra_hour_rate = extra_hour_rate or _safe_float(package.extra_hour_rate)
        driver_bata = driver_bata or _safe_float(package.driver_bata_default)
        night_charges = night_charges or _safe_float(package.night_charge_default)
        permit_amount = permit_amount or _safe_float(package.permit_default)
        state_tax_amount = state_tax_amount or _safe_float(package.state_tax_default)
        minimum_km_per_day = minimum_km_per_day if minimum_km_per_day is not None else package.minimum_km_per_day
        km_rate = km_rate or _safe_float(package.km_rate)

        if category == "local":
            included_km = package.included_km
            included_hours = package.included_hours
            hours_used = _calculate_hours_used(start_time, end_time)
            if distance_km is not None and included_km is not None:
                extra_km = max(0.0, distance_km - float(included_km))
            if hours_used is not None and included_hours is not None:
                extra_hours = max(0.0, hours_used - float(included_hours))
            extra_km_amount = extra_km * extra_km_rate if extra_km is not None else 0.0
            extra_hour_amount = extra_hours * extra_hour_rate if extra_hours is not None else 0.0
        elif "300 km" in category or "average" in category:
            days_used = _calculate_days_used(start_time, end_time)
            included_km = minimum_km_per_day * days_used if days_used is not None and minimum_km_per_day is not None else None
            if distance_km is not None and included_km is not None:
                extra_km = max(0.0, distance_km - float(included_km))
            extra_km_amount = extra_km * extra_km_rate if extra_km is not None else 0.0
            extra_hour_amount = 0.0
        elif category == "outstation":
            if distance_km is not None:
                extra_km = distance_km
            extra_km_amount = None
            extra_hour_amount = 0.0
            package_amount = package_amount or 0.0
        else:
            if distance_km is not None and minimum_km_per_day is not None:
                extra_km = max(0.0, distance_km - float(minimum_km_per_day))
            extra_km_amount = extra_km * extra_km_rate if extra_km is not None else 0.0
            extra_hour_amount = 0.0
    else:
        if distance_km is not None and km_rate is not None:
            extra_km = distance_km
            extra_km_amount = distance_km * km_rate
        extra_hour_amount = 0.0

    distance_charge = None
    if package and _normalize_category(package.package_category) == "outstation" and distance_km is not None:
        distance_charge = distance_km * km_rate

    grand_total = float(package_amount)
    grand_total += _safe_float(extra_km_amount)
    grand_total += _safe_float(extra_hour_amount)
    grand_total += driver_bata
    grand_total += night_charges
    grand_total += permit_amount
    grand_total += state_tax_amount
    grand_total += toll_amount
    grand_total += parking_amount

    if distance_charge is not None:
        grand_total = distance_charge + driver_bata + night_charges + permit_amount + state_tax_amount + toll_amount + parking_amount

    explicit_trip_revenue = values.get("trip_revenue")
    if explicit_trip_revenue is not None:
        grand_total = float(explicit_trip_revenue)

    return {
        "package_name": package.name if package else None,
        "trip_date": trip_date,
        "distance_km": distance_km,
        "included_km": included_km,
        "included_hours": included_hours,
        "hours_used": hours_used,
        "days_used": days_used,
        "extra_km": extra_km,
        "extra_hours": extra_hours,
        "package_amount": package_amount,
        "extra_km_amount": extra_km_amount,
        "extra_hour_amount": extra_hour_amount,
        "driver_bata": driver_bata,
        "night_charges": night_charges,
        "permit_amount": permit_amount,
        "state_tax_amount": state_tax_amount,
        "toll_amount": toll_amount,
        "parking_amount": parking_amount,
        "grand_total": grand_total,
        "trip_revenue": float(explicit_trip_revenue) if explicit_trip_revenue is not None else grand_total,
    }
