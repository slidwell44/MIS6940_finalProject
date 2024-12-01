from pydantic import BaseModel, Field


class WorkorderRequest(BaseModel):
    WorkorderNumber: str = Field(default="WO12345")
    Revision: str = Field(default="1A")
    Quantity: float = Field(default=5.00)
