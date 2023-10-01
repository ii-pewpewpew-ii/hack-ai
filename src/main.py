from uagents import Agent,Bureau
from agents.currency.currency import agent as currency_agent

if __name__ == "__main__":
    bureau = Bureau(endpoint="http://127.0.0.1:8000/submit", port=8000)
    print(f"Adding currency agent to Bureau {currency_agent.address}")
    bureau.add(currency_agent)
    bureau.run()