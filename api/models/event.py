from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import date, datetime, time, timedelta
from .pydanticclasses.pydanticobjectid import PydanticObjectId
from .memberclass import MemberClass
from bson.binary import Binary, UUID_SUBTYPE
from uuid import uuid4

class Event(BaseModel):
    id: Binary = Binary(bytes(bytearray(uuid4().bytes)), UUID_SUBTYPE)
    title: Dict[str, str] # store translations
    description: Dict[str, str]
    created: datetime = datetime.now()
    starttime: datetime
    endtime: Optional[datetime]
    signupfrom: timedelta = timedelta(seconds=0) # if equals 0, signup is not restricted
    boats: List[PydanticObjectId] = [] # if boats is empty, maxparticipants has to be used
    maxparticipants: int = 0
    allowedmemberclasses: List[PydanticObjectId] = [] # if empty, all members can sign up.