from uagents import Model
from pydantic import Field

class NewsRequest(Model):
    
    '''
    This class is used for defining a request to the news agent.

    Attributes:
        currency_1 (str) : First currency to be present in the article title.
        currency_2 (str) : Second currency to be present in the article title.
        subscription_id (str) : The subscription that needed the article fetch.
    '''

    currency_1 : str = Field(description='First currency to be present in the article title')
    currency_2 : str = Field(description='Second currency to be present in the article title')
    subscription_id : str = Field(description='The subscription that needed the article fetch')
