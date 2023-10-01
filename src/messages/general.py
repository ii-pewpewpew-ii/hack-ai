from uagents import Model
from pydantic import Field
from enum import Enum
from typing import List,Optional

class UAgentResponseType(Enum):
    ERROR = "error"
    OPTIONS = "available_options"
    SUCCESS = "response_successfull"
    ALERT = "threshold_exceeded"

class KeyValue(Model):
    key : str 
    value : str

class UAgentResponse(Model):
    type : UAgentResponseType = Field(description="The type of response generated or error")
    request_id : Optional[str] = Field(description= "Request for which this response was generated")
    message : str = Field(description="The response message, if any was generated for the request")
    available_options : Optional[List[KeyValue]]= Field(description="Options attached if the response requires any")
    subscriber_id : Optional[str] = Field(description="Incase the response requires for the subscriber id to be attached")