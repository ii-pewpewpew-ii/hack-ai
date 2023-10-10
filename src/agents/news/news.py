from uagents import Agent, Protocol, Context
from utils.summarizer import generate_summary, text_extractor_from_website
from dotenv import load_dotenv
import requests
import os
from uagents.setup import fund_agent_if_low
from messages.news_request import NewsRequest
from messages.general import UAgentResponse,UAgentResponseType
import json

load_dotenv('.\.env')

NEWS_AGENT_SEED = os.getenv('NEWS_AGENT_SEED',"secret-news-agent-seed")
NEWS_API_KEY = os.getenv('NEWS_API_KEY',"")
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

    response_string=""
    summary="\n\nThe possible reason based on articles found online are:\n"

    if data['articles']:
        response_string=""

        for i,article in enumerate(data['articles']):
            response_string+=text_extractor_from_website(article['url'])
        
        summary+=generate_summary(response_string)
    else:
        summary="\n\nNo related articles found\n"
    
    reply = UAgentResponse(type=UAgentResponseType.NEWS,message=summary,subscriber_id=subscription_id)
    await ctx.send(sender,reply)


agent.include(protocol=news_protocol)