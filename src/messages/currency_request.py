from uagents import Model
from pydantic import Field

class AvailableCurrenciesRequest(Model):

    '''
    This class is used for defining a request to the currency agent
    that enquires about the supported currencies.

    Attributes:
        from_ (str) : Sender id for the request.
        request_id (str) : Request id for the request.
    '''

    from_ : str = Field(description= "Sender id for the request")
    request_id : str = Field(description="Request id for the request")

class SubscribeRequest(Model):

    '''
    This class is used for defining a request to the currency agent
    that requests a subscription for alerts.

    Attributes:
        subscriber_address (str) : Sender address for the request.
        currency_base (str) : Base currency to be tracked.
        currency_exchanged (str) : Currency to which conversion should be tracked.
        upper_bound (float) : The upper bound, which when crossed should initiate a notification to the subscriber.
        lower_bound (float) : The lower bound, which when crossed should initiate a notification to the subscriber.
        request_id (str) : Request id for the request.
    '''

    subscriber_address : str = Field(description="Sender id for the request")
    currency_base : str = Field(description="Base currency to be tracked")
    currency_exchanged : str = Field(description="Currency to which conversion should be tracked")
    upper_bound : float = Field(description="The upper bound, which when crossed should initiate a notification to the subscriber")
    request_id : str = Field(description="Request id for the request")
    lower_bound : float = Field(description="The lower bound, which when crossed should initiate a notification to the subscriber")
    