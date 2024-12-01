from pydantic import BaseModel, Field


class WorkorderRequest(BaseModel):
    WorkorderNumber: str = Field(
        default=None,
        description="The unique identifier for the workorder."
    )
    Revision: str = Field(
        default=None,
        description="The revision code of the workorder."
    )
    Quantity: float = Field(
        default=None,
        description="The quantity associated with the workorder."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "WorkorderNumber": "WO12345",
                "Revision": "1A",
                "Quantity": 5.00
            }
        }
