from uagents import Agent, Protocol,Context
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv
import os, json, uuid
from messages.general import UAgentResponse,UAgentResponseType,KeyValue
from messages.currency_request import SubscribeRequest,AvailableCurrenciesRequest
from messages.news_request import NewsRequest
import requests
from agents.news.news import agent as news_agent
import datetime


load_dotenv(".\.env")

FIXER_API_KEY = os.getenv("FIXER_API_KEY","") 
FIXER_API_URL = "http://data.fixer.io/api"
assert FIXER_API_KEY, "fixer api key is missing"

agent = Agent(
    name = "currency-tracker",
    seed = "CURRENCY_SEED",
)

agent._storage._path='./data/agent_data.json'

fund_agent_if_low(agent.wallet.address())

currency_protocol = Protocol("Currency-rates")


@currency_protocol.on_interval(period=86400)
async def fetch_available_rates(ctx : Context):

    '''
    This function is called with a period of 1 Day.

    It is used to find the available currency exchanges 
    supported by the backend API.

    Args : 
        ctx (Context) : Context Object

    Returns :
        None 
    '''

    response = requests.get(url = FIXER_API_URL+'/symbols',params = {"access_key" : FIXER_API_KEY})
    
    if not response.json()['success']:
        print("Failed Request, try again later",response.json())
    else:
        data = response.json()
        available_currencies = data["symbols"]
        agent._storage.set('currencies',available_currencies)
    

@currency_protocol.on_interval(period=60)
async def news_fetch(ctx : Context):

    '''
    This function is called every minute since the API updates 
    the ForEx rates every minute.

    Proceeds to call the handle_news_fetch function when the rates are fetched.

    Args : 
        ctx (Context) : Context 

    Returns :
        None 
    '''

    response = requests.get(url=FIXER_API_URL + "/latest",params = {"access_key" : FIXER_API_KEY})
    
    if response.status_code != 200:
        ctx.logger.info("Couldn't fetch details due to error : ",response.status_code)
    else:
        await handle_news_fetch(ctx = ctx,response = response)


@currency_protocol.on_message(model = AvailableCurrenciesRequest,replies = UAgentResponse)
async def handle_available_currencies_request(ctx : Context,sender : str,msg : AvailableCurrenciesRequest):
    
    '''
    This function is called when the currency agent receives a 
    request for available currencies.

    Function also sends the client a list of supported currencies.

    Args : 
        ctx (Context) : Context Object
        sender (str) : Address of the sender
        msg (AvailableCurrenciesRequest) : AvailableCurrenciesRequest message sent by the client

    Returns :
        None 
    '''

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


@currency_protocol.on_message(model = SubscribeRequest,replies=UAgentResponse)
async def handle_subscribe_request(ctx : Context,sender : str,msg : SubscribeRequest):
    
    '''
    This function is called when the currency agent 
    receives a request for adding a subscription.

    Sends the client a SUCCESS Response once the subscription is added.

    Args : 
        ctx (Context) : Context Object
        sender (str) : Address of the sender
        msg (SubscriRequest) : SubscribeRequest message sent by the client

    Returns :
        None 
    '''

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
        "upper_bound" : msg.upper_bound,
        "subscriber_address" : msg.subscriber_address,
        "lower_bound" : msg.lower_bound
    }
    ctx.storage.set(subscriber_id,subscriber_data)
    
    data = json.dumps({
        "currency_base" : msg.currency_base,
        "currency_exchange" : msg.currency_exchanged ,
        "upper_bound" : msg.upper_bound,
        "lower_bound" : msg.lower_bound 
    })

    response = UAgentResponse(type=UAgentResponseType.SUCCESS,request_id=request_id,message=data,subscriber_id=subscriber_id)
    await ctx.send(sender,response)


@currency_protocol.on_message(model=UAgentResponse,replies=None)
async def handle_notifications(ctx : Context,sender : str, msg : UAgentResponse):
    
    '''
    This function is called when the news agent 
    responds with the appropriate data.

    Sends the alert to the client associated with the respective subscription id.

    Args : 
        ctx (Context) : Context 
        sender (str) : NEWS Agent Address
        msg (UAgentResponse) : response generated by the News agent

    Returns :
        None 
    '''
    
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
    
    '''
    This function iterates through the list of subscriptions available
    and checks if the current ForEx rate has crossed bounds for any of 
    the active subscriptions.

    If found to cross bounds, initiates a request to the News agent for
    fetching related articles

    Args : 
        ctx (Context) : Context 

    Returns :
        None 
    '''

    data = response.json()

    if not data['success']:
        return 

    rates = data["rates"]
    ctx.storage.set('rates',rates)
    subscribers = ctx.storage.get("subscribers")

    if not subscribers:
        return 
    
    for subscriber_id in subscribers:
        subscription_data = ctx.storage.get(subscriber_id)
        base = subscription_data["currency_base"]
        exchange = subscription_data["currency_exchange"]
        upper_bound = subscription_data["upper_bound"]
        lower_bound = subscription_data["lower_bound"]
        current_value = calculate_exchange(base=base,exchange=exchange,rates=rates)

        if current_value >= upper_bound or current_value < lower_bound:
            news_agent_address = news_agent.address
            news_request = NewsRequest(currency_1=base,currency_2=exchange,subscription_id=subscriber_id)
            await ctx.send(news_agent_address,news_request)


def calculate_exchange(base : str,exchange : str,rates : dict) -> float:
    
    '''
    This function is called to calculate the exchange rate

    Args : 
        base (str) : Base currency symbol
        exchange (str) : Foreign currency symbol
        rates (dict) : Map of the rates fetched from the API 

    Returns :
        current_value (float) : calculated current exchange value  
    '''

    base_rate = rates[base]
    exchange_rate = rates[exchange]

    base_to_eur = 1/base_rate
    current_value = base_to_eur * exchange_rate

    return current_value


def format_alert(subscription_id : str,subscription_data : dict,rates : dict) -> str:
    
    '''
    This function is called to format the alert message for the client.

    Args : 
        subscription_id (str) : Subscription id.
        subscription_data (dict) : Map of subscription related data.
        rates (dict) : Map of the rates fetched from the API. 

    Returns :
        reply (str) : Formatted reply string.  
    '''

    base = subscription_data["currency_base"]
    exchange = subscription_data["currency_exchange"]
    lower_bound = subscription_data["lower_bound"]
    upper_bound = subscription_data["upper_bound"]
    current_value = calculate_exchange(base,exchange,rates)
    current_timestamp = datetime.datetime.now()

    reply = f"Alert for currency out of bounds\nTimestamp:{current_timestamp}\nSubscription Id : {subscription_id}\nTracking {base} -> {exchange}\n"
    if current_value < lower_bound:
        reply += f"Set lower-bound : {lower_bound}\nCurrent-Value : {current_value}"
    else:
        reply += f"Set upper-bound : {upper_bound}\nCurrent-Value : {current_value}"
    return reply


agent.include(currency_protocol)