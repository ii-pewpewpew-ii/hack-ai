from uagents import Model
from pydantic import Field

class NewsRequest(Model):
    currency_1 : str = Field(description='First currency to be present in the article title')
    currency_2 : str = Field(description='Second currency to be present in the article title')
    subscription_id : str = Field(description='The subscription that needed the article fetch')
