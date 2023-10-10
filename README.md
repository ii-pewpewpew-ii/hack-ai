# Multiple-currency monitoring system: Using Fetch-ai uagents

## Project description

> This project was made for IIT Bombay's Techfest'23: HackAI competition

Real-time monitoring of foreign currencies with respect to a base currency is done. Notifications are sent if the currency value goes out of bounds. News articles explaining the reason for the change in currency value, if available, will be summarized and sent to the user along with the notification. A front-end is also developed for user-friendly interaction with the agent.

## Getting it started

### Pre-requisites
To run this project, you would need:

* Make sure you have python installed in your system. It is preferred to have a python version `>=3.10`
  
* You will also need poetry package. To install, run
  
  ```
  pip install poetry
  ```
### Setting up the runtime environment
* Clone the project to your local system. This can be done by running

  ```
  git clone <repo_url>
  ```
  Here, <repo_url> can be taken from the Code button given in this Github repo.

* Navigate into the project

  ```
  cd <project_name>
  ```
* Use the command `poetry install` to install all the necessary packages for the project. This will install the required packages.
  
### Update .env file
Before running the project, you should provide API key values in the `.env` file provided. The following API keys are needed for the project to run:
* **FIXER API KEY**: For getting currency exchange rates. [Fixer API Key](https://fixer.io/documentation)
* **FIXER API KEY**: For getting currency exchange rates. [Fixer API Key](https://fixer.io/documentation)
* **FIXER API KEY**: For getting currency exchange rates. [Fixer API Key](https://fixer.io/documentation)
* **OPENAI API KEY**: Used in the project for summarizing the news articles. [OpenAI API Key](https://platform.openai.com/docs/api-reference/introduction)
### Run the project
* Create another terminal with the same path and enter the following commands
  ```
  cd src
  python main.py
  ```
  * Now run the following command in the terminal with the project path
  ```
  python frontend.py
  ```
## Features
