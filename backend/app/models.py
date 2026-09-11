from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), default="PS5")
    image: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    price_try: Mapped[float] = mapped_column(Float, nullable=False)
    old_price_try: Mapped[float | None] = mapped_column(Float, nullable=True)
    discount_percent: Mapped[int] = mapped_column(Integer, default=0)
    store_url: Mapped[str] = mapped_column(String(1200), default="")
    external_id: Mapped[str] = mapped_column(String(300), unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tier: Mapped[str] = mapped_column(String(30), nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    image: Mapped[str] = mapped_column(String(1000), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    price_try: Mapped[float | None] = mapped_column(Float, nullable=True)
    store_url: Mapped[str] = mapped_column(String(1200), default="")
    external_id: Mapped[str] = mapped_column(String(300), unique=True, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
