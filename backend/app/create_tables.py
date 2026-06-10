from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir))

from app.database import engine
from app.models import Base

Base.metadata.create_all(bind=engine)

print("Tables Created Successfully")