from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class WorkorderResponse(BaseModel):
    Id: UUID = Field(default_factory=uuid4)
    WorkorderNumber: str = Field(default="WO12345")
    Revision: str = Field(default="1A")
    Quantity: float = Field(default=5.00)
