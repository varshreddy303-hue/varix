from .. import schemas as legacy_schemas
from .auth import AuthTokenResponse, LoginRequest, RefreshTokenRequest, UserCreate, UserResponse
from .booking import BookingAvailabilityResponse, BookingCreate, BookingResponse, BookingUpdate
from .calendar import CalendarEventResponse
from .customer import CustomerCreate, CustomerUpdate, CustomerResponse
from .maintenance import MaintenanceScheduleCreate, MaintenanceScheduleResponse, MaintenanceScheduleUpdate
from .organization import OrganizationRegistrationRequest, OrganizationResponse
from .reminder import (
    NotificationEventResponse,
    NotificationPreferenceCreate,
    NotificationPreferenceResponse,
    ReminderResponse,
    ReminderRuleCreate,
    ReminderRuleResponse,
    ReminderRuleUpdate,
)
from .trip import TripCompleteRequest, TripCreate, TripResponse, TripUpdate
from .vehicle import (
    VehicleAvailabilityResponse,
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
    VehicleUpcomingEMIResponse,
)
from .expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from .invoice import InvoiceCreate, InvoiceResponse, InvoiceUpdate
from .profit import TripProfitResponse, VehicleDailyProfitResponse, VehicleMonthlyProfitResponse, ProfitSummaryResponse

# Re-export legacy schema objects (e.g., VehicleCreate)
try:
    VehicleCreate = legacy_schemas.VehicleCreate
except Exception:
    pass
