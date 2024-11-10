from enum import Enum
from pydantic import BaseModel
from uuid import uuid4, UUID


class Status(Enum):
    NOTSTARTED = 'NOTSTARTED'
    INPROGRESS = 'INPROGRESS'
    COMPLETED = 'COMPLETED'


class WorkOrder(BaseModel):
    WorkOrderId: UUID = uuid4()
    WorkOrderNumber: str
    WorkOrderDescription: str
    WorkOrderStatus: Status = Status.NOTSTARTED
