"""
Dependencias reutilizables para el recurso Loan.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.models.loan_model import Loan
from app.schemas.loan_schema import LoanCreate
from app.services import device_service, loan_service, user_service


def get_loan_or_404(loan_id: int, db: Session = Depends(get_db)) -> Loan:
    """Busca un préstamo por ID y lanza 404 automáticamente si no existe."""
    db_loan = loan_service.get_loan_by_id(db, loan_id)
    if db_loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Préstamo no encontrado",
        )
    return db_loan


def validate_loan_creation(
    loan_data: LoanCreate,
    db: Session = Depends(get_db),
) -> LoanCreate:
    """
    Valida, antes de crear un préstamo, que:
    - El usuario exista.
    - El dispositivo exista.
    - El dispositivo esté disponible.
    """
    db_user = user_service.get_user_by_id(db, loan_data.user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    db_device = device_service.get_device_by_id(db, loan_data.device_id)
    if db_device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado",
        )

    if not db_device.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El dispositivo no está disponible para préstamo",
        )

    return loan_data


def validate_loan_not_returned(db_loan: Loan = Depends(get_loan_or_404)) -> Loan:
    """
    Valida, antes de procesar una devolución, que el préstamo
    no haya sido devuelto previamente. Depende de get_loan_or_404,
    formando una cadena: primero existencia, luego regla de negocio.
    """
    if db_loan.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este préstamo ya fue devuelto anteriormente",
        )
    return db_loan