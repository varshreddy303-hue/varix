from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db.models import (
    Trip,
    Expense,
    TripProfitSummary,
    VehicleDailyProfit,
    VehicleMonthlyProfit,
)


def get_trip_profit_summary(db: Session, trip_id: int, organization_id: Optional[str] = None) -> Optional[TripProfitSummary]:
    query = db.query(TripProfitSummary).filter(TripProfitSummary.trip_id == trip_id)
    if organization_id:
        query = query.filter(TripProfitSummary.organization_id == organization_id)
    return query.first()


def list_vehicle_daily_profit(
    db: Session,
    vehicle_id: int,
    organization_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 50,
) -> Tuple[List[VehicleDailyProfit], int]:
    query = db.query(VehicleDailyProfit).filter(VehicleDailyProfit.vehicle_id == vehicle_id)
    if organization_id:
        query = query.filter(VehicleDailyProfit.organization_id == organization_id)
    total = query.count()
    items = query.order_by(VehicleDailyProfit.profit_date.desc()).offset(offset).limit(limit).all()
    return items, total


def list_vehicle_monthly_profit(
    db: Session,
    vehicle_id: int,
    organization_id: Optional[str] = None,
    offset: int = 0,
    limit: int = 50,
) -> Tuple[List[VehicleMonthlyProfit], int]:
    query = db.query(VehicleMonthlyProfit).filter(VehicleMonthlyProfit.vehicle_id == vehicle_id)
    if organization_id:
        query = query.filter(VehicleMonthlyProfit.organization_id == organization_id)
    total = query.count()
    items = query.order_by(VehicleMonthlyProfit.year.desc(), VehicleMonthlyProfit.month.desc()).offset(offset).limit(limit).all()
    return items, total


def get_profit_summary(db: Session, organization_id: Optional[str] = None) -> Tuple[float, float, float]:
    query = db.query(
        func.coalesce(func.sum(TripProfitSummary.trip_revenue), 0),
        func.coalesce(func.sum(TripProfitSummary.total_expense), 0),
        func.coalesce(func.sum(TripProfitSummary.trip_profit), 0),
    )
    if organization_id:
        query = query.filter(TripProfitSummary.organization_id == organization_id)
    total_revenue, total_expense, total_profit = query.one()
    return float(total_revenue), float(total_expense), float(total_profit)


def get_or_create_trip_profit_summary(db: Session, trip_id: int, organization_id: str):
    summary = get_trip_profit_summary(db, trip_id, organization_id)
    if summary:
        return summary
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.organization_id == organization_id).first()
    if not trip:
        return None
    summary = TripProfitSummary(
        organization_id=trip.organization_id,
        trip_id=trip.id,
        vehicle_id=trip.vehicle_id,
        trip_revenue=float(trip.trip_revenue or 0),
        total_expense=0.0,
        trip_profit=float(trip.trip_revenue or 0),
        profit_date=trip.start_time.date() if trip.start_time else trip.created_at.date(),
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary
