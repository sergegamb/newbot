from pydantic import BaseModel, Field
from typing import List, Optional
from bs4 import BeautifulSoup



# 'technician': {'email_id': 'mikhaylov@agneko.com', 'phone': None, 'name': 'Александр Михайлов', 
class Technician(BaseModel):
    email_id: str = Field(..., alias="email_id")
    name: str = Field(..., alias="name")
    
# 'status': {'color': '#efb116', 'name': 'На согласовании', 'id': '1201'}
class Status(BaseModel):
    color: Optional[str] = Field(..., alias="color")
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

    @property
    def emoji(self):
        if self.status.name == "Открыта":
            return "🔴"
        if self.status.name == "Запланирована":
            return "🔵"
        if self.status.name == "Выполнена":
            return "🟣"
        if self.status.name == "Назначена":
            return "⚪️"
        if self.status.name == "В работе":
            return "🟠"
        if self.status.name == "Ожидание информации":
            return "🟢"
        if self.status.name == "На согласовании":
            return "🟡"
        return "-"

    
class ListInfo(BaseModel):
    total_count: int = Field(..., alias="total_count")


class RequestsResponse(BaseModel):
    response_status: str = Field(..., alias="response_status")
    list_info: ListInfo = Field(..., alias="list_info")
    requests: List[Request] = Field(..., alias="requests")


class From(BaseModel):
    name: str = Field(..., alias="name")
    id: str = Field(..., alias="id")


class SentTime(BaseModel):
    display_value: str = Field(..., alias="display_value")


class Conversation(BaseModel):
    from_: From = Field(..., alias="from")
    id: int = Field(..., alias="id")
    sent_time: SentTime = Field(..., alias="sent_time")


class Notification(BaseModel):
    id: str = Field(..., alias="id")
    description: str = Field(..., alias="description")

    @property
    def text(self):
        description = self.description.replace("<br />", "\n")
        soup = BeautifulSoup(description, 'html.parser')
        description = soup.get_text()
        return description