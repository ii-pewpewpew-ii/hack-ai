from uagents import Model
from pydantic import Field

class AvailableCurrenciesRequest(Model):
    from_ : str = Field(description= "Sender id for the request")
    request_id : str = Field(description="Request id for the request")

class SubscribeRequest(Model):
    subscriber_address : str = Field(description="Sender id for the request")
    currency_base : str = Field(description="Base currency to be tracked")
    currency_exchanged : str = Field(description="Currency to which conversion should be tracked")
    threshold : float = Field(description="The threshold, which when crossed should initiate a notification to the subscriber")
    request_id : str = Field(description="Request id for the request")
