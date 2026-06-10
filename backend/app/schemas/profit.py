from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TripProfitResponse(BaseModel):
    trip_id: int
    vehicle_id: int
    trip_revenue: float
    total_expense: float
    trip_profit: float
    profit_date: date

    model_config = ConfigDict(from_attributes=True)


class VehicleDailyProfitResponse(BaseModel):
    vehicle_id: int
    profit_date: date
    total_revenue: float
    total_expense: float
    total_profit: float

    model_config = ConfigDict(from_attributes=True)


class VehicleMonthlyProfitResponse(BaseModel):
    vehicle_id: int
    year: int
    month: int
    total_revenue: float
    total_expense: float
    total_profit: float

    model_config = ConfigDict(from_attributes=True)


class ProfitSummaryResponse(BaseModel):
    total_revenue: float
    total_expense: float
    total_profit: float

    model_config = ConfigDict(from_attributes=True)
