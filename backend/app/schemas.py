
from datetime import datetime

from pydantic import BaseModel, Field


class SaleCreate(BaseModel):
    product: str = Field(min_length=1, max_length=100)
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class SaleResponse(BaseModel):
    id: int
    product: str
    quantity: int
    unit_price: float
    total_amount: float
    sale_date: datetime

    model_config = {"from_attributes": True}
