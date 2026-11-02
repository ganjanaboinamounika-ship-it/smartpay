from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.payments import router as payments_router
from app.api.v1.rbac import router as rbac_router
from app.core.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "SMARTPAY is an educational payment processing "
        "and fraud detection API."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)


app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    rbac_router,
    prefix="/api/v1",
)

app.include_router(
    payments_router,
    prefix="/api/v1",
)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "Welcome to SMARTPAY API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
def health_check():
    return {
        "success": True,
        "status": "healthy",
    }
