from uagents import Agent, Protocol,Context
from pydantic import Field
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv
import os
import uuid
from messages.general import UAgentResponse,UAgentResponseType,KeyValue
from messages.currency_request import SubscribeRequest,AvailableCurrenciesRequest
import requests
from typing import List

load_dotenv("D:\hackAi\.env")



FIXER_API_KEY = os.getenv("FIXER_API_KEY","") 
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
    if response != 200:
        print("Failed Request, try again later",response.json())
    else:
        data = response.json()
        available_currencies = data["symbols"]
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
    response = UAgentResponse(type=UAgentResponseType.SUCCESS,request_id=request_id,message="Subscription added. Notification will be sent if threshold is exceeded.",subscriber_id=subscriber_id)
    await ctx.send(sender,response)


#API Updates rates every 60 seconds. Hence to fetch the data and check against all subscribers to send them notification in case of exceeded threshold.
@currency_protocol.on_interval(period=60)
async def check_and_send_notifications(ctx : Context):
    response = requests.get(url=FIXER_API_URL + "/latest",params = {"access_key" : FIXER_API_KEY})
    if response.status_code != 200:
        ctx.logger.info("Couldn't fetch details due to error : ",response.status_code)
        return
    else:
        data = response.json()
        rates = data["rates"]
        subscribers = ctx.storage.get("subscribers")
        if not subscribers:
            return 
        for subscriber in subscribers:
            subscription_data = ctx.storage.get(subscriber)
            base = subscription_data["currency_base"]
            exchange = subscription_data["currency_exchange"]
            subscriber_address = subscription_data["subscriber_address"]
            threshold = subscription_data["threshold"]

            base_rate = rates[base]
            exchange_rate = rates[exchange]
            base_to_eur = 1/base_rate
            current_value = base_to_eur * exchange_rate
            if current_value >= threshold:
                alert = UAgentResponse(type= UAgentResponseType.ALERT,message=f"Threshold exceeded for subscription Id : {subscriber}\nTracking {base} -> {exchange}\nSet-Threshold : {threshold}\nCurrent-Value : {current_value}",subscriber_id=subscriber)
                await ctx.send(subscriber_address,alert)


agent.include(currency_protocol)