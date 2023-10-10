from uagents import Model
from pydantic import Field
from enum import Enum
from typing import List,Optional

class UAgentResponseType(Enum):

    '''
    This class is used to define the type of response sent by the agent.

    Attributes:
        ERROR (str) : Error message.
        OPTIONS (str) : Available options message.
        SUCCESS (str) : Success message.
        ALERT (str) : Alert message.
        NEWS (str) : News message.
    '''

    ERROR = "error"
    OPTIONS = "available_options"
    SUCCESS = "response_successfull"
    ALERT = "threshold_exceeded"
    NEWS = "news_data"

class KeyValue(Model):
    
    '''
    This class is used for defining key value pairs.

    Attributes:
        key (str) : Key attribute.
        value (str) : Value for the corresponding key.
    '''

    key : str 
    value : str

class UAgentResponse(Model):

    '''
    This class is used for defining a response message.

    Attributes:
        type (str) : Type of response.
        request_id (str) : Request for which this response was generated.
        message (str) : The response message generated for the request.
        available_options (List[KeyValue]) : Options attached if the response requires any.
        subscriber_id (str) : Incase the response requires for the subscriber id to be attached.
    '''

    type : UAgentResponseType = Field(description="The type of response generated or error")
    request_id : Optional[str] = Field(description= "Request for which this response was generated")
    message : str = Field(description="The response message, if any was generated for the request")
    available_options : Optional[List[KeyValue]]= Field(description="Options attached if the response requires any")
    subscriber_id : Optional[str] = Field(description="Incase the response requires for the subscriber id to be attached")