from pydantic import BaseModel, Field
from typing import List, Optional


# 'technician': {'email_id': 'mikhaylov@agneko.com', 'phone': None, 'name': 'Александр Михайлов', 
class Technician(BaseModel):
    email_id: str = Field(..., alias="email_id")
    name: str = Field(..., alias="name")
    
# 'status': {'color': '#efb116', 'name': 'На согласовании', 'id': '1201'}
class Status(BaseModel):
    color: str = Field(..., alias="color")
    name: str = Field(..., alias="name")
    id: str = Field(..., alias="id")

# 'color': '#006600', 'name': 'Normal', 'id': '2'}
class Priority(BaseModel):
    color: str = Field(..., alias="color")
    name: str = Field(..., alias="name")
    id: str = Field(..., alias="id")

class Request(BaseModel):
    id: int = Field(..., alias="id")
    subject: str = Field(..., alias="subject")
    description: Optional[str] = Field(None, alias="description")
    status: Status = Field(..., alias="status")
    technician: Optional[Technician] = Field(None, alias="technician")
    # date: str = Field(..., alias="date")
    priority: Optional[Priority] = Field(None, alias="priority")

    @property
    def url(self):
        return "https://support.agneko.com/WorkOrder.do?woMode=viewWO&woID=" + self.id.__str__()
    
class ListInfo(BaseModel):
    total_count: int = Field(..., alias="total_count")
    
class RequestsResponse(BaseModel):
    status: str = Field(..., alias="status")
    list_info: ListInfo = Field(..., alias="list_info")
    requests: List[Request] = Field(..., alias="requests")
