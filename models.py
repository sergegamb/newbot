from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from pydantic import BaseModel, Field
from typing import List, Optional
from bs4 import BeautifulSoup
import sc



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
    
    @property
    def callback(self):
        return "request_" + self.id.__str__()
    
    @property
    def text(self):
        text = f"*{self.subject}*\n"
        if self.status:
            text += f"Status: {self.status.name}\n"
        if self.technician:
            text += f"Technician: {self.technician.name}\n"
        if self.priority:
            text += f"Priority: {self.priority.name}\n"
        #TODO: add due date, contract & account
        if self.description:
            description = self.description
            description = description.replace("<br />", "\n")
            soup = BeautifulSoup(description, 'html.parser')
            description = soup.get_text()
            text += f"\n{description}"
        return text

    @property
    def keyboard(self):
        keyboard = []
        keyboard.append([InlineKeyboardButton("Description", callback_data=f"description"),
                        InlineKeyboardButton("Add task" , callback_data="add_task")])
            #TODO: add quick actions
            #TODO: add assign dialog
            #TODO: add reply option
            #TODO: add edit menu
            #TODO: add add note dialog
            #TODO: add menu
                #TODO: add Properties
                #TODO: add Resolution
                #TODO: add Time entry
                #TODO: add History
                #TODO: add Tasks
                #TODO: add Approvals
        request_conversations = sc.get_request_conversation(self.id)
        for conversation in request_conversations:
            keyboard.append([InlineKeyboardButton(f"{conversation.from_.name}  {conversation.sent_time.display_value}", callback_data=f"conversation_{conversation.id}")])
        
        keyboard.append([])
        keyboard.append([InlineKeyboardButton("<- Back", callback_data="back"),
            InlineKeyboardButton(f"Open #{self.id} in browser", url=self.url)])
        return InlineKeyboardMarkup(keyboard)

    
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
    

class TRequest(BaseModel):
    subject: str = Field(..., alias="subject")
    id: int = Field(..., alias="id")


class DueByTime(BaseModel):
    display_value: str = Field(..., alias="display_value")
    value: str = Field(..., alias="value")


class Task(BaseModel):
    id: int = Field(..., alias="id")
    title: str = Field(..., alias="title")
    description: Optional[str] = Field(None, alias="description")
    status: Status = Field(..., alias="status")
    owner: Optional[Technician] = Field(..., alias="owner")
    request: Optional[TRequest] = Field(None, alias="request")
    due_by_time: Optional[DueByTime] = Field(None, alias="due_by_time")
    
    

    @property
    def subject(self):
        return self.title

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
    
    @property
    def callback(self):
        if self.request:
            return "requesttask_" + self.request.id.__str__() + "_" + self.id.__str__()
        return "task" + self.id.__str__()
    
    @property
    def text(self):
        text = f"*{self.subject}*\n"
        if self.status:
            text += f"Status: {self.status.name}\n"
        if self.owner:
            text += f"Owner: {self.owner.name}\n"
        if self.request:
            text += f"Request: {self.request.subject}\n"
        if self.due_by_time:
            text += f"Due date: {self.due_by_time.display_value}\n"
        if self.description:
            description = self.description
            description = description.replace("<br />", "\n")
            soup = BeautifulSoup(description, 'html.parser')
            description = soup.get_text()
            text += f"\n{description}"
        return text

    @property
    def url(self):
        return "https://support.agneko.com/ui/tasks?mode=detail&from=showAllTasks&module=request&taskId=" + self.id.__str__() + "&moduleId=" + self.request.id.__str__()
        
    @property
    def keyboard(self):
        keyboard = []
        if self.description is None:
            keyboard.append([InlineKeyboardButton("Provide description", callback_data=f"task_description_add")])
        keyboard.append([InlineKeyboardButton("Back", callback_data=f"back"),
                         InlineKeyboardButton("Open in browser", url=self.url)])
        return InlineKeyboardMarkup(keyboard)
