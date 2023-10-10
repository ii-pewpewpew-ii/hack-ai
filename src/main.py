from uagents import Agent,Bureau
from agents.currency.currency import agent as currency_agent
from agents.news.news import agent as news_agent
import json
import os

#to say currency address to user agents 
def update_address(address):
    f = open("data/config.json")
    temp = json.load(f)
    temp["currency_agent_address"] = address 
    temp = json.dumps(temp)
    with open("data/config.json","w") as w:
        w.write(temp)

#clear agent json before starts 
def clear_json():
     
    agent_file = [i for i in os.listdir("data") if i.endswith(".json") and i!="config.json"][0]
    
    with open(agent_file,"w") as f :
        json.dump({},f)

if __name__ == "__main__":
    print(os.listdir())
    clear_json()
    
    bureau = Bureau(endpoint=["http://127.0.0.1:8001/submit"], port=8001)

    print(f"Adding currency agent to Bureau {currency_agent.address}")

    address = currency_agent.address
    update_address(address)

    bureau.add(currency_agent)
    bureau.add(news_agent)

    bureau.run()

