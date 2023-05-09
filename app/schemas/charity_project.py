from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt


class CharityProjectBase(BaseModel):
    """Базовая схема."""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None)
    full_amount: Optional[PositiveInt]

    class Config:
        extra = Extra.forbid
        min_anystr_length = 1


class CharityProjectCreate(CharityProjectBase):
    """Схема для полученных данных."""
    name: str = Field(..., max_length=100)
    description: str = Field(..., )
    full_amount: PositiveInt


class CharityProjectDB(CharityProjectBase):
    """Схема для возвращаемого объекта."""
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True


class CharityProjectUpdate(CharityProjectBase):
    """Схема для полученных данных."""

    class Config:
        extra = Extra.forbid
