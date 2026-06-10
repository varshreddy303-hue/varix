from fastapi import APIRouter

from .routers.auth import router as auth_router
from .routers.bookings import router as bookings_router
from .routers.calendar import router as calendar_router
from .routers.customers import router as customers_router
from .routers.maintenance import router as maintenance_router
from .routers.organizations import router as organizations_router
from .routers.vehicles import router as vehicles_router
from .routers.trips import router as trips_router
from .routers.expenses import router as expenses_router
from .routers.invoices import router as invoices_router
from .routers.profits import router as profits_router
from .routers.reminders import router as reminders_router
from .routers.packages import router as packages_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(organizations_router)
router.include_router(customers_router)
router.include_router(vehicles_router)
router.include_router(bookings_router)
router.include_router(calendar_router)
router.include_router(maintenance_router)
router.include_router(trips_router)
router.include_router(expenses_router)
router.include_router(invoices_router)
router.include_router(profits_router)
router.include_router(reminders_router)
router.include_router(packages_router)
