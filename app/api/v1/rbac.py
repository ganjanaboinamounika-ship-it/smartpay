from fastapi import APIRouter, Depends

from app.api.dependencies import require_roles
from app.models import User, UserRole


router = APIRouter(
    prefix="/rbac",
    tags=["RBAC"],
)


@router.get("/customer-test")
def customer_test(
    current_user: User = Depends(
        require_roles(UserRole.CUSTOMER)
    ),
):
    return {
        "success": True,
        "message": "Customer role authorized",
        "user_id": current_user.id,
        "role": current_user.role.value,
    }


@router.get("/admin-test")
def admin_test(
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    ),
):
    return {
        "success": True,
        "message": "Admin role authorized",
        "user_id": current_user.id,
        "role": current_user.role.value,
    }


@router.get("/fraud-analyst-test")
def fraud_analyst_test(
    current_user: User = Depends(
        require_roles(UserRole.FRAUD_ANALYST)
    ),
):
    return {
        "success": True,
        "message": "Fraud analyst role authorized",
        "user_id": current_user.id,
        "role": current_user.role.value,
    }