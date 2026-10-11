from sqlalchemy import (
    Boolean,
    DECIMAL,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Disruption(Base):
    __tablename__ = "disruptions"

    disruption_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True
    )

    disruption_type: Mapped[str] = mapped_column(String(100))
    industry: Mapped[str] = mapped_column(String(100))
    supplier_tier: Mapped[str] = mapped_column(String(50))
    supplier_region: Mapped[str] = mapped_column(String(100))
    supplier_size: Mapped[str] = mapped_column(String(50))

    has_backup_supplier: Mapped[bool] = mapped_column(Boolean)

    disruption_severity: Mapped[str] = mapped_column(String(50))


class Impact(Base):
    __tablename__ = "impact"

    disruption_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("disruptions.disruption_id"),
        primary_key=True
    )

    production_impact_pct: Mapped[float] = mapped_column(
        DECIMAL(10, 2)
    )

    revenue_loss_usd: Mapped[float] = mapped_column(
        DECIMAL(15, 2)
    )


class Response(Base):
    __tablename__ = "response"

    disruption_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("disruptions.disruption_id"),
        primary_key=True
    )

    response_type: Mapped[str] = mapped_column(String(100))

    response_time_days: Mapped[int] = mapped_column(
        Integer
    )


class Recovery(Base):
    __tablename__ = "recovery"

    disruption_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("disruptions.disruption_id"),
        primary_key=True
    )

    partial_recovery_days: Mapped[int] = mapped_column(
        Integer
    )

    full_recovery_days: Mapped[int] = mapped_column(
        Integer
    )

    permanent_supplier_change: Mapped[bool] = mapped_column(
        Boolean
    )