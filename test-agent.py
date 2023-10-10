from uagents import Agent, Context, Model, Bureau
from enum import Enum
from pydantic import Field
import uuid
from src.messages.currency_request import AvailableCurrenciesRequest, SubscribeRequest
from src.messages.general import UAgentResponse,KeyValue,UAgentResponseType
from uagents.setup import fund_agent_if_low

client = Agent(name = "client",seed = "alice phase",port=8008,endpoint=["http://127.0.0.1:8008/submit"])
currency_agent_address = "agent1q20cgjnqr3jczjqpz897rslwus6cffs0xsac66d6ux0smu6zyvddcrec3u7"

fund_agent_if_low(client.wallet.address())
available_currencies_request = str(uuid.uuid4())

base_currency = "USD"
foreign_currency = "AED,COP"
foreign_currency=foreign_currency.split(',')


@client.on_interval(period= 100)
async def handler(ctx : Context):
    await ctx.send(currency_agent_address,AvailableCurrenciesRequest(from_ = client.address,request_id=available_currencies_request))


@client.on_message(model=UAgentResponse,replies=SubscribeRequest)
async def handle_currencies_response(ctx:Context,sender : str,msg: UAgentResponse):
    if msg.type == UAgentResponseType.ERROR:
        ctx.logger.info("Cannot fetch details now")
        return
    elif msg.type == UAgentResponseType.OPTIONS:
        ctx.logger.info("Available Currencies : ")
        keys = set()
        for key_value_pair in msg.available_options:
            keys.add(key_value_pair.key)
        if base_currency in keys and all(item in keys for item in foreign_currency):
            #Multiple foreign currency request
            for forCur in foreign_currency:
                subscribe_request_id = str(uuid.uuid4())
                await ctx.send(sender,SubscribeRequest(subscriber_address=client.address,currency_base=base_currency,currency_exchanged=forCur,threshold=100,request_id=subscribe_request_id))
        else:
            ctx.logger.info("Currency not found in registry. Nothing can be done")

    elif msg.type == UAgentResponseType.SUCCESS:
        ctx.logger.info(f"Subscribed successfully with id {msg.message}")
    elif msg.type == UAgentResponseType.ALERT:
        ctx.logger.info(msg.message)


client.run()

# bureau = Bureau()
# bureau.add(client)
# if __name__ == "__main__":
#     bureau.run()