from uagents import Agent,Protocol,Context
import requests
import os
from uagents.setup import fund_agent_if_low
from messages.news_request import NewsRequest
from messages.general import UAgentResponse,UAgentResponseType
import json

# load_dotenv('D:\hackAi\.env')

NEWS_AGENT_SEED = "secret_news_agent_seed"

## 
NEWS_API_KEY = "3c8cbc85fa724034bb31e01ebf9d95f7"

NEWS_API_URL = 'https://newsapi.org/v2/everything'

assert NEWS_API_KEY, 'News api key not found.'

agent = Agent(
    name="news-agent",
    seed=NEWS_AGENT_SEED
)
fund_agent_if_low(agent.wallet.address())

news_protocol = Protocol("news_protocol")

@news_protocol.on_message(model=NewsRequest,replies=UAgentResponse)
async def handle_request(ctx : Context,sender : str,msg : NewsRequest):
    
    currency_1 = msg.currency_1
    currency_2 = msg.currency_2
    subscription_id = msg.subscription_id

    response = requests.get(NEWS_API_URL,params={"q" : f"{currency_1} AND {currency_2}","apiKey" : NEWS_API_KEY,'language' : 'en', 'sortBy' : 'publishedAt','searchIn' : 'title',"pageSize" : 2})
    data = response.json()

    reply_message_json = json.dumps(data['articles'])
    
    reply = UAgentResponse(type=UAgentResponseType.NEWS,message=reply_message_json,subscriber_id=subscription_id)
    await ctx.send(sender,reply)


agent.include(protocol=news_protocol)