from uagents import Agent, Protocol,Context
from pydantic import Field
from uagents.setup import fund_agent_if_low
# from dotenv import load_dotenv
import os
import json
import uuid
from messages.general import UAgentResponse,UAgentResponseType,KeyValue
from messages.currency_request import SubscribeRequest,AvailableCurrenciesRequest
from messages.news_request import NewsRequest
import requests
from agents.news.news import agent as news_agent
from typing import List

# load_dotenv("D:\hackAi\.env")

FIXER_API_KEY = "af32a45ef1d4dff2ab98a3c0100e8c77"

##### 
assert FIXER_API_KEY, "fixer api key is missing"

FIXER_API_URL = "http://data.fixer.io/api"

agent = Agent(
    name = "currency-tracker",
    seed = "CURRENCY_SEED",
)
fund_agent_if_low(agent.wallet.address())

currency_protocol = Protocol("Currency-rates")

# Fetching available currencies in the api everyday to update available currency options
@currency_protocol.on_interval(period=86400)
async def fetch_available_rates(ctx : Context):
    response = requests.get(url = FIXER_API_URL+'/symbols',params = {"access_key" : FIXER_API_KEY})
    
    if not response.json()['success']:
        print("Failed Request, try again later",response.json())
    else:
        data = response.json()
        available_currencies = data["symbols"]
        print(available_currencies)
        agent._storage.set('currencies',available_currencies)
    

# Sending the client a list of all available currencies that the agent can track.
@currency_protocol.on_message(model = AvailableCurrenciesRequest,replies = UAgentResponse)
async def handle_available_currencies_request(ctx : Context,sender : str,msg : AvailableCurrenciesRequest):

    available_currencies = ctx.storage.get("currencies")
    request_id = msg.request_id
    response = None
    
    if not available_currencies:
        response = UAgentResponse(type=UAgentResponseType.ERROR,request_id=request_id,message="Currency Archive not available, try again later")
    else:
        options = list()
        for key,value in available_currencies.items():
           options.append(KeyValue(key=key,value=value))
        response = UAgentResponse(type=UAgentResponseType.OPTIONS,request_id=request_id,message="Currently available currency options",available_options=options)

    await ctx.send(sender,response)


# Adding the subscription to the agent's storage when a subscription request is received
@currency_protocol.on_message(model = SubscribeRequest,replies=UAgentResponse)
async def handle_subscribe_request(ctx : Context,sender : str,msg : SubscribeRequest):

    subscriber_id = str(uuid.uuid4())
    subscribers = ctx.storage.get('subscribers')
    request_id = msg.request_id

    if not subscribers : 
        ctx.storage.set('subscribers',[subscriber_id])
    else:
        subscribers.append(subscriber_id)
        ctx.storage.set('subscribers',subscribers)
        
    subscriber_data = {
        "currency_base" : msg.currency_base,
        "currency_exchange":msg.currency_exchanged,
        "threshold" : msg.threshold,
        "subscriber_address" : msg.subscriber_address
    }
    ctx.storage.set(subscriber_id,subscriber_data)
    
    data = json.dumps({
        "currency_base" : msg.currency_base,
        "currency_exchange" : msg.currency_exchanged ,
        "threshold" : msg.threshold 
    })

    response = UAgentResponse(type=UAgentResponseType.SUCCESS,request_id=request_id,message=data,subscriber_id=subscriber_id)
    await ctx.send(sender,response)


#API Updates rates every 60 seconds. Hence to fetch the data and check against all subscribers to send them notification in case of exceeded threshold.
@currency_protocol.on_interval(period=15)
async def news_fetch(ctx : Context):
    
    response = requests.get(url=FIXER_API_URL + "/latest",params = {"access_key" : FIXER_API_KEY})
    
    if response.status_code != 200:
        ctx.logger.info("Couldn't fetch details due to error : ",response.status_code)
    else:
        await handle_news_fetch(ctx = ctx,response = response)
    

@currency_protocol.on_message(model=UAgentResponse,replies=None)
async def handle_notifications(ctx : Context,sender : str, msg : UAgentResponse):
    
    if msg.type == UAgentResponseType.NEWS:
        subscription_id = msg.subscriber_id
        subscriber_details = ctx.storage.get(subscription_id)
        subscriber_address = subscriber_details['subscriber_address']
        rates = ctx.storage.get('rates')
        news =msg.message

        reply_message = format_alert(subscription_id=subscription_id,subscription_data=subscriber_details,rates=rates) + news
        response = UAgentResponse(type=UAgentResponseType.ALERT,message=reply_message,subscriber_id=subscription_id)

        await ctx.send(subscriber_address,response)


async def handle_news_fetch(ctx : Context,response : requests.Response):
    
    data = response.json()

    print(data)

    if not data['success']:
        return 

    rates = data["rates"]
    ctx.storage.set('rates',rates)
    subscribers = ctx.storage.get("subscribers")

    if not subscribers:
            return 
    
    for subscriber_id in subscribers:
        print(subscriber_id)
        subscription_data = ctx.storage.get(subscriber_id)
        base = subscription_data["currency_base"]
        exchange = subscription_data["currency_exchange"]
        threshold = subscription_data["threshold"]

        current_value = calculate_exchange(base=base,exchange=exchange,rates=rates)

        if current_value >= threshold:
            news_agent_address = news_agent.address
            news_request = NewsRequest(currency_1=base,currency_2=exchange,subscription_id=subscriber_id)

            await ctx.send(news_agent_address,news_request)


def calculate_exchange(base : str,exchange : str,rates : dict) -> float:
    
    base_rate = rates[base]
    exchange_rate = rates[exchange]

    base_to_eur = 1/base_rate
    current_value = base_to_eur * exchange_rate

    return current_value


def format_alert(subscription_id : str,subscription_data : dict,rates : dict) -> str:
    
    base = subscription_data["currency_base"]
    exchange = subscription_data["currency_exchange"]
    threshold = subscription_data["threshold"]

    current_value = calculate_exchange(base,exchange,rates)

    return f"Threshold exceeded for subscription Id : {subscription_id}\nTracking {base} -> {exchange}\nSet-Threshold : {threshold}\nCurrent-Value : {current_value}"


agent.include(currency_protocol)