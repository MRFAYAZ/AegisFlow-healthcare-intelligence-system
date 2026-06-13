from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.api.routes.medicines import (
    router as medicine_router
)

from app.api.routes.facilities import (
    router as facility_router
)

from app.api.routes.inventory import (
    router as inventory_router
)

from app.api.routes.alerts import (
    router as alert_router
)

from app.api.routes.emergencies import (
    router as emergency_router
)

from app.api.routes.redistribution import(
    router as redistribution_router
)
    
from app.api.routes.dashboard import (
    router as dashboard_router
)

from app.api.routes.auth import (
    router as auth_router
)

from app.api.routes.users import (
    router as users_router
)

from app.api.routes.facility_users import (
    router as facility_user_router
)

from app.api.routes.audit_logs import (
    router as audit_logs_router
)

from app.api.routes.event_logs import (
    router as event_logs_router
)

from app.api.routes.user_sessions import (
    router as user_sessions_router
)
# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="AegisFlow Healthcare Intelligence System",
    version="1.0.0",
    description="Healthcare Supply Intelligence Platform"
)
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)

# =========================================================
# ROUTES
# =========================================================

app.include_router(
    medicine_router,
    prefix="/api/v1"
)

app.include_router(
    facility_router,
    prefix="/api/v1"
)

app.include_router(
    inventory_router,
    prefix="/api/v1"
)

app.include_router(
    alert_router,
    prefix="/api/v1"
)

app.include_router(
    emergency_router,
    prefix="/api/v1"
)

app.include_router(
    redistribution_router,
    prefix="/api/v1"
)

app.include_router (
    dashboard_router,
    prefix="/api/v1"
)

app.include_router(
    auth_router,
    prefix="/api/v1"
)

app.include_router(
    users_router,
    prefix="/api/v1"
)

app.include_router (
    facility_user_router,
    prefix="/api/v1"
)

app.include_router(
    audit_logs_router,
    prefix="/api/v1"
)

app.include_router(
    event_logs_router,
    prefix="/api/v1"
)

app.include_router(
    user_sessions_router,
    prefix="/api/v1"
)
# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def health_check():

    return {
        "application": "AegisFlow",
        "status": "running",
        "version": "1.0.0"
    }
