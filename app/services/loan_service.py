"""
Capa de servicios para el recurso Loan.
Contiene la lógica de negocio: creación de préstamos, devoluciones
y consultas con filtros, incluyendo el efecto sobre Device.is_available.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import (
    DeviceBasicInfo,
    LoanCreate,
    LoanDetailResponse,
    UserBasicInfo,
)


def create_loan(db: Session, loan_data: LoanCreate) -> Loan:
    """
    Crea un nuevo préstamo con status 'active' y marca el dispositivo
    asociado como no disponible. Ambas operaciones se confirman
    en una sola transacción (un solo commit).
    """
    db_loan = Loan(
        user_id=loan_data.user_id,
        device_id=loan_data.device_id,
        status="active",
    )
    db.add(db_loan)

    db_device = db.query(Device).filter(Device.id == loan_data.device_id).first()
    db_device.is_available = False

    db.commit()
    db.refresh(db_loan)
    return db_loan


def return_loan(db: Session, db_loan: Loan) -> Loan:
    """
    Marca un préstamo como devuelto: asigna return_date, cambia el status
    a 'returned' y vuelve a marcar el dispositivo como disponible.
    """
    db_loan.status = "returned"
    db_loan.return_date = datetime.now(timezone.utc)

    db_device = db.query(Device).filter(Device.id == db_loan.device_id).first()
    db_device.is_available = True

    db.commit()
    db.refresh(db_loan)
    return db_loan


def get_all_loans(
    db: Session,
    status_filter: Optional[str] = None,
    user_id: Optional[int] = None,
    device_id: Optional[int] = None,
) -> list[Loan]:
    """Lista préstamos con filtros opcionales por estado, usuario o dispositivo."""
    query = db.query(Loan)

    if status_filter is not None:
        query = query.filter(Loan.status == status_filter)

    if user_id is not None:
        query = query.filter(Loan.user_id == user_id)

    if device_id is not None:
        query = query.filter(Loan.device_id == device_id)

    return query.all()


def get_loan_by_id(db: Session, loan_id: int) -> Optional[Loan]:
    return db.query(Loan).filter(Loan.id == loan_id).first()


def get_loans_by_user(db: Session, user_id: int) -> list[Loan]:
    """Consulta todos los préstamos asociados a un usuario específico."""
    return db.query(Loan).filter(Loan.user_id == user_id).all()


def get_loans_by_device(db: Session, device_id: int) -> list[Loan]:
    """Consulta todos los préstamos asociados a un dispositivo específico (histórico)."""
    return db.query(Loan).filter(Loan.device_id == device_id).all()


def _to_loan_detail(db_loan: Loan) -> LoanDetailResponse:
    """
    Construye manualmente un LoanDetailResponse a partir de un objeto Loan,
    aprovechando las relaciones ORM (loan.user, loan.device) en vez de
    hacer consultas adicionales.
    """
    return LoanDetailResponse(
        loan_id=db_loan.id,
        status=db_loan.status,
        loan_date=db_loan.loan_date,
        return_date=db_loan.return_date,
        user=UserBasicInfo.model_validate(db_loan.user),
        device=DeviceBasicInfo.model_validate(db_loan.device),
    )


def get_all_loans_with_details(
    db: Session,
    status_filter: Optional[str] = None,
    user_email: Optional[str] = None,
    device_type: Optional[str] = None,
) -> list[LoanDetailResponse]:
    """
    Consulta préstamos con join explícito a User y Device, permitiendo
    filtrar por campos de las tablas relacionadas (email, tipo de dispositivo)
    además del propio status del préstamo.
    """
    query = (
        db.query(Loan)
        .join(User, Loan.user_id == User.id)
        .join(Device, Loan.device_id == Device.id)
    )

    conditions = []
    if status_filter is not None:
        conditions.append(Loan.status == status_filter)
    if user_email is not None:
        conditions.append(User.email.ilike(user_email))
    if device_type is not None:
        conditions.append(Device.device_type == device_type)

    if conditions:
        query = query.filter(and_(*conditions))

    db_loans = query.all()
    return [_to_loan_detail(loan) for loan in db_loans]