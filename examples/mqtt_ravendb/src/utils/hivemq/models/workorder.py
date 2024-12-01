from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SerialNumber:
    serialnumber: str


@dataclass
class Operation:
    operation: str


@dataclass
class WorkOrder:
    orderNumber: str
    partNumber: str
    partRev: str
    partDescription: str
    plant: str
    cell: str
    orderType: str
    planRev: str
    fileName: str
    faiRequired: str
    serialRequired: str
    serialTransferRequired: str
    units: str
    qty: int
    leadTime: str
    needDate: str
    startDate: str
    releasedBy: str
    releasedDate: str
    updatedBy: str
    updatedDate: str
    operations: List[Operation] = field(default_factory=list)
    serialNumbers: List[SerialNumber] = field(default_factory=list)
    scrapAttrition: Optional[int] = None

    @classmethod
    def from_dict(cls, data):
        serial_numbers = [SerialNumber(**sn) for sn in data.get('serialNumbers', [])]
        operations = [Operation(**op) for op in data.get('operations', [])]
        return cls(
            orderNumber=data.get('orderNumber'),
            partNumber=data.get('partNumber'),
            partRev=data.get('partRev'),
            partDescription=data.get('partDescription'),
            plant=data.get('plant'),
            cell=data.get('cell'),
            orderType=data.get('orderType'),
            planRev=data.get('planRev'),
            fileName=data.get('fileName'),
            faiRequired=data.get('faiRequired'),
            serialRequired=data.get('serialRequired'),
            serialTransferRequired=data.get('serialTransferRequired'),
            units=data.get('units'),
            qty=data.get('qty'),
            serialNumbers=serial_numbers,
            scrapAttrition=data.get('scrapAttrition'),
            leadTime=data.get('leadTime'),
            needDate=data.get('needDate'),
            startDate=data.get('startDate'),
            releasedBy=data.get('releasedBy'),
            releasedDate=data.get('releasedDate'),
            updatedBy=data.get('updatedBy'),
            updatedDate=data.get('updatedDate'),
            operations=operations
        )
