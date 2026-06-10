from datetime import date
from typing import Any, Dict, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db.models import (
    Trip,
    Expense,
    TripProfitSummary,
    VehicleDailyProfit,
    VehicleMonthlyProfit,
    TripStatusEnum,
    User,
)
from ..repositories import profit_repository


def _get_profit_date(trip: Trip) -> date:
    return trip.start_time.date() if trip.start_time else trip.created_at.date()


def _calculate_trip_profit(trip: Trip) -> Tuple[float, float, float]:
    expense_total = float(
        trip and trip.expenses and sum([float(exp.amount) for exp in trip.expenses]) or 0.0
    )
    trip_revenue = float(trip.trip_revenue or 0.0)
    trip_profit = trip_revenue - expense_total
    return trip_revenue, expense_total, trip_profit


def _rebuild_vehicle_aggregates(db: Session, vehicle_id: int, organization_id: str) -> None:
    daily_rows = (
        db.query(
            TripProfitSummary.profit_date,
            func.coalesce(func.sum(TripProfitSummary.trip_revenue), 0).label('total_revenue'),
            func.coalesce(func.sum(TripProfitSummary.total_expense), 0).label('total_expense'),
            func.coalesce(func.sum(TripProfitSummary.trip_profit), 0).label('total_profit'),
        )
        .filter(
            TripProfitSummary.vehicle_id == vehicle_id,
            TripProfitSummary.organization_id == organization_id,
        )
        .group_by(TripProfitSummary.profit_date)
        .order_by(TripProfitSummary.profit_date.desc())
    )
    db.query(VehicleDailyProfit).filter(
        VehicleDailyProfit.vehicle_id == vehicle_id,
        VehicleDailyProfit.organization_id == organization_id,
    ).delete()
    for row in daily_rows:
        db.add(
            VehicleDailyProfit(
                organization_id=organization_id,
                vehicle_id=vehicle_id,
                profit_date=row.profit_date,
                total_revenue=float(row.total_revenue),
                total_expense=float(row.total_expense),
                total_profit=float(row.total_profit),
            )
        )

    monthly_rows = (
        db.query(
            TripProfitSummary.year,
            TripProfitSummary.month,
            func.coalesce(func.sum(TripProfitSummary.trip_revenue), 0).label('total_revenue'),
            func.coalesce(func.sum(TripProfitSummary.total_expense), 0).label('total_expense'),
            func.coalesce(func.sum(TripProfitSummary.trip_profit), 0).label('total_profit'),
        )
        .filter(
            TripProfitSummary.vehicle_id == vehicle_id,
            TripProfitSummary.organization_id == organization_id,
        )
        .group_by(TripProfitSummary.year, TripProfitSummary.month)
        .order_by(TripProfitSummary.year.desc(), TripProfitSummary.month.desc())
    )
    db.query(VehicleMonthlyProfit).filter(
        VehicleMonthlyProfit.vehicle_id == vehicle_id,
        VehicleMonthlyProfit.organization_id == organization_id,
    ).delete()
    for row in monthly_rows:
        db.add(
            VehicleMonthlyProfit(
                organization_id=organization_id,
                vehicle_id=vehicle_id,
                year=row.year,
                month=row.month,
                total_revenue=float(row.total_revenue),
                total_expense=float(row.total_expense),
                total_profit=float(row.total_profit),
            )
        )
    db.commit()


def _update_trip_profit_summary(db: Session, trip_id: int, organization_id: str) -> TripProfitSummary:
    trip = (
        db.query(Trip)
        .filter(Trip.id == trip_id, Trip.organization_id == organization_id)
        .first()
    )
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

    trip_revenue, total_expense, trip_profit = _calculate_trip_profit(trip)
    profit_date = _get_profit_date(trip)
    year = profit_date.year
    month = profit_date.month

    summary = profit_repository.get_trip_profit_summary(db, trip_id, organization_id)
    if not summary:
        summary = TripProfitSummary(
            organization_id=trip.organization_id,
            trip_id=trip.id,
            vehicle_id=trip.vehicle_id,
            trip_revenue=trip_revenue,
            total_expense=total_expense,
            trip_profit=trip_profit,
            profit_date=profit_date,
            year=year,
            month=month,
        )
        db.add(summary)
    else:
        summary.trip_revenue = trip_revenue
        summary.total_expense = total_expense
        summary.trip_profit = trip_profit
        summary.profit_date = profit_date
        summary.year = year
        summary.month = month
    db.commit()
    db.refresh(summary)

    db.query(VehicleDailyProfit).filter(
        VehicleDailyProfit.vehicle_id == summary.vehicle_id,
        VehicleDailyProfit.organization_id == organization_id,
        VehicleDailyProfit.profit_date == summary.profit_date,
    ).delete()
    db.add(
        VehicleDailyProfit(
            organization_id=organization_id,
            vehicle_id=summary.vehicle_id,
            profit_date=summary.profit_date,
            total_revenue=summary.trip_revenue,
            total_expense=summary.total_expense,
            total_profit=summary.trip_profit,
        )
    )
    db.commit()

    _rebuild_vehicle_aggregates(db, summary.vehicle_id, organization_id)
    return summary


def recalculate_trip_profit(db: Session, trip_id: int, organization_id: str) -> TripProfitSummary:
    return _update_trip_profit_summary(db, trip_id, organization_id)


def get_trip_profit_service(db: Session, trip_id: int, current_user: User) -> TripProfitSummary:
    organization_id = str(current_user.organization_id)
    summary = profit_repository.get_trip_profit_summary(db, trip_id, organization_id)
    if not summary:
        summary = _update_trip_profit_summary(db, trip_id, organization_id)
    return summary


def list_vehicle_daily_profit_service(
    db: Session,
    vehicle_id: int,
    current_user: User,
    page: int = 1,
    page_size: int = 25,
) -> Tuple[list[VehicleDailyProfit], int]:
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")
    organization_id = str(current_user.organization_id)
    offset = (page - 1) * page_size
    return profit_repository.list_vehicle_daily_profit(
        db,
        vehicle_id=vehicle_id,
        organization_id=organization_id,
        offset=offset,
        limit=page_size,
    )


def list_vehicle_monthly_profit_service(
    db: Session,
    vehicle_id: int,
    current_user: User,
    page: int = 1,
    page_size: int = 25,
) -> Tuple[list[VehicleMonthlyProfit], int]:
    if page < 1 or page_size < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination parameters")
    organization_id = str(current_user.organization_id)
    offset = (page - 1) * page_size
    return profit_repository.list_vehicle_monthly_profit(
        db,
        vehicle_id=vehicle_id,
        organization_id=organization_id,
        offset=offset,
        limit=page_size,
    )


def get_profit_summary_service(db: Session, current_user: User) -> dict[str, float]:
    organization_id = str(current_user.organization_id)
    total_revenue, total_expense, total_profit = profit_repository.get_profit_summary(db, organization_id)
    return {
        "total_revenue": total_revenue,
        "total_expense": total_expense,
        "total_profit": total_profit,
    }
