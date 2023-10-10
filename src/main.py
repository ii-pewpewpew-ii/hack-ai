from uagents import Agent,Bureau
from agents.currency.currency import agent as currency_agent
from agents.news.news import agent as news_agent
import json

def update_address(address):
    f = open("config.json")
    temp = json.load(f)
    temp["currency_agent_address"] = address 
    temp = json.dumps(temp)
    with open("config.json","w") as w:
        w.write(temp)

if __name__ == "__main__":
    bureau = Bureau(endpoint=["http://127.0.0.1:8001/submit"], port=8001)

    print(f"Adding currency agent to Bureau {currency_agent.address}")

    address = currency_agent.address
    update_address(address)

    bureau.add(currency_agent)
    bureau.add(news_agent)
    bureau.run()

