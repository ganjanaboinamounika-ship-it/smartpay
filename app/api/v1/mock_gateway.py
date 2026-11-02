from fastapi import APIRouter

from app.services.mock_gateway_service import process_mock_payment


router = APIRouter(
    prefix="/mock-gateway",
    tags=["Mock Payment Gateway"],
)


@router.post("/payment")
def mock_payment():
    return process_mock_payment()