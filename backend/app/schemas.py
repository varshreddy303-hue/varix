from pydantic import BaseModel

class VehicleCreate(BaseModel):
    vehicle_number: str
    vehicle_type: str
    model: str