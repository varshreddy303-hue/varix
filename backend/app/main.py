from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .router import router as api_router
from .services.reminder_scheduler import start_reminder_scheduler

app = FastAPI(title="VahanOne API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Welcome to VahanOne"}


@app.on_event("startup")
def startup_tasks() -> None:
    if settings.enable_reminder_scheduler:
        start_reminder_scheduler()


app.include_router(api_router)