from uagents import Agent, Protocol, Context
from utils.summarizer import generate_summary, text_extractor_from_website
from dotenv import load_dotenv
import requests
import os
from uagents.setup import fund_agent_if_low
from messages.news_request import NewsRequest
from messages.general import UAgentResponse,UAgentResponseType

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
    
    '''
    This function is called when it receives a News request from the 
    currency agent.

    Fetches related news articles from the NEWS API for the reason
    behind the currency going out of bounds and sends it to the currency agent.

    Args : 
        ctx (Context) : Context.
        sender (str) : Currency agent address.
        msg (NewsRequest) : The news request initiated by the currency agent.
    Returns :
        None 
    '''

    currency_1 = msg.currency_1
    currency_2 = msg.currency_2
    subscription_id = msg.subscription_id

    response = requests.get(NEWS_API_URL,params={"q" : f"{currency_1} vs {currency_2}","apiKey" : NEWS_API_KEY, 'sortBy' : 'publishedAt','searchIn' : 'description'})
    data = response.json()

    response_string=""
    summary="\n\nThe possible reason based on articles found online are:\n"

    if data and data['status']!='error':
        response_string=""

        for i,article in enumerate(data['articles']):
            # Limit to a maximum of 4 articles
            if i==3:
                break
            response_string+=text_extractor_from_website(article['url'])
        
        summary+=generate_summary(response_string, currency_1, currency_2)
    else:
        summary="\n\nNo related articles found\n"
    
    print(response_string)
    reply = UAgentResponse(type=UAgentResponseType.NEWS,message=summary,subscriber_id=subscription_id)
    await ctx.send(sender,reply)


agent.include(protocol=news_protocol)