"""
Rutas del recurso /loans.
Define los endpoints HTTP y delega la lógica a loan_service.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.dependencies.loan_dependencies import (
    get_loan_or_404,
    validate_loan_creation,
    validate_loan_not_returned,
)
from app.dependencies.auth_dependency import get_current_active_user, require_roles
from app.models.loan_model import Loan
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse, LoanStatus
from app.services import loan_service
from fastapi import Request  # agregar al import existente
from app.middlewares.rate_limiter import limiter

router = APIRouter(prefix="/loans", tags=["Préstamos"])


@router.post(
    "",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear préstamo",
    description="Crea un préstamo, validando que el usuario y el dispositivo existan "
    "y que el dispositivo esté disponible. Marca el dispositivo como no disponible.",
    response_description="Préstamo creado con estado 'active'; el dispositivo queda marcado como no disponible.",
    responses={
        404: {"description": "Usuario o dispositivo no encontrado"},
        409: {"description": "El dispositivo no está disponible"},
    },
)
@limiter.limit("10/minute")
def create_loan(
    request: Request,
    loan_data: LoanCreate = Depends(validate_loan_creation),
    db: Session = Depends(get_db),
    _: object = Depends(get_current_active_user),
):
    return loan_service.create_loan(db, loan_data)


@router.get(
    "/details",
    response_model=list[LoanDetailResponse],
    summary="Listar préstamos con información relacionada",
    response_description="Lista de préstamos con los datos del usuario y del dispositivo anidados.",

    description="Lista préstamos con datos embebidos de usuario y dispositivo (join). "
    "Permite filtrar por estado, correo del usuario o tipo de dispositivo.",
)
def list_loans_with_details(
    status_filter: Optional[LoanStatus] = Query(
        default=None, alias="status", description="Filtrar por estado del préstamo"
    ),
    user_email: Optional[str] = Query(default=None, description="Filtrar por correo del usuario"),
    device_type: Optional[str] = Query(default=None, description="Filtrar por tipo de dispositivo"),
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("admin", "support")),
):
    status_value = status_filter.value if status_filter is not None else None
    return loan_service.get_all_loans_with_details(
        db, status_filter=status_value, user_email=user_email, device_type=device_type
    )
    
@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    summary="Consultar préstamo por ID",
    response_description="Datos del préstamo solicitado.",
    responses={404: {"description": "Préstamo no encontrado"}},
)
def get_loan(db_loan: Loan = Depends(get_loan_or_404)):
    return db_loan


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Registrar devolución de préstamo",
    description="Marca un préstamo como devuelto, asigna la fecha de devolución "
    "y vuelve a marcar el dispositivo como disponible.",
    response_description="Préstamo actualizado con estado 'returned' y fecha de devolución; el dispositivo vuelve a estar disponible.",
    responses={
        404: {"description": "Préstamo no encontrado"},
        409: {"description": "El préstamo ya fue devuelto anteriormente"},
    },
)
def return_loan(
    db_loan: Loan = Depends(validate_loan_not_returned),
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("admin", "support")),
):
    return loan_service.return_loan(db, db_loan)