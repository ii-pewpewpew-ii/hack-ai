# Multiple-currency monitoring system: Using Fetch-ai uagents

## Project description

> This project was made for IIT Bombay's Techfest'23: HackAI competition 🚀

Real-time monitoring of foreign currencies with respect to a base currency is done. Notifications are sent if the currency value goes out of bounds. News articles explaining the reason for the change in currency value, if available, will be summarized and sent to the user along with the notification. A front-end is also developed for user-friendly interaction with the agent.

## 🚀 Getting it started

### 🔍 Pre-requisites

To run this project, you would need:

* *Python 3.x:* Make sure you have python installed in your system. It is preferred to have a python version `>=3.10`
  
* *Poetry:* You will also need poetry package. To install, run
  
  ```
  pip install poetry
  ```
  
### 🔧 Setting up the runtime environment

* Clone the project to your local system. This can be done by running

  ```
  git clone <repo_url>
  ```
  Here, <repo_url> can be taken from the Code button given in this Github repo.

* Navigate into the project

  ```
  cd <project_name>
  ```
  
* Use the following command to install all the necessary packages for the project. This will install the required packages.

  ```
  poetry install
  ```
  
* Use the following command to activate the poetry virtual environment. 

  ```
  poetry shell
  ```
  
### Update .env file

Before running the project, you should provide API key values in the `.env` file provided. The following API keys are needed for the project to run:

* **FIXER API KEY** : For getting currency exchange rates.
  
   #### Steps to get the FIXER API KEY
  
  * Go to the fixer api website. [Fixer API Key](https://fixer.io/documentation)
    
  * Click on the `Get Free API Key` button
    
  * Choose the free plan and enter the required details.
    
  * The API key will be displayed in your dashboard. Copy and paste it in your `.env` file
  
* **NEWS API KEY** : To get relevant articles for knowing about the reason for changes in currency rate. 
  
    #### Steps to get the NEWS API KEY
    
    * Go to the NEWS api website. [NEWS API Key](https://newsapi.org/s/google-news-api)
      
    * Click on the `Get API Key` button.
      
    * Enter the required details.
      
    * The API key will be displayed in your dashboard. Copy and paste it in your `.env` file
    
* **OPENAI API KEY** : Used in the project for summarizing the news articles. [OpenAI API Key](https://platform.openai.com/docs/api-reference/introduction)

   #### Steps to get the OPENAI API KEY
    
    * Go to the OpenAI website. [OpenAI website](https://platform.openai.com/)
      
    * Click on `View API keys` from your profile button on the top-right.
      
    * You might find your exisiting API keys there. If not present, click on `Create new secret key`
      
    * Copy the generated secret key.
      
    * There is a high chance that the usage limit might be reached or the token might have been expired(Free tier tokens might have been expired).
 
    * To verify, go to billing and check on `Credits Remaining`. If no credits remain, add a payment method and pay for using the API key.
 
    > If there is no credit remaining for the API key, you might not be able to use it
  
### 📜 Run the project

* Create another terminal with the same path and enter the following commands. 
  #### Run this before running frontend.py 

* Create another terminal with the project root directory and enter the following commands. Ensure that the poetry virtual environment is activated.
  
  ```
  cd src
  python main.py
  ```
  
* Now run the following command in another terminal with the project root directory. Ensure that the poetry virtual environment is activated.
  
  ```
  python frontend.py
  ```
  
## ✨ Features

* A user-friendly GUI for interacting with the uagents, subscribing to various currency exchange values and getting notifications about the out-of-bound value of a specific currency exchange.
  
  ![image](https://github.com/ii-pewpewpew-ii/hack-ai/assets/47415114/36302be2-6031-46b4-99da-96972f2e34ee)

* Reasoning for the change in exchange rate will also be provided if possible by using NEWS APIs to get relevant articles. The relevant articles are summarized to get the required reasoning.
  
  ![image](https://github.com/ii-pewpewpew-ii/hack-ai/assets/47415114/ac192aa3-5720-4258-88c6-4a12658c4e36)

* Users can set upper bound and lower bound for a given pair of base and foreign currency. Multiple such pairs can be added at the same time.
  
  ![image](https://github.com/ii-pewpewpew-ii/hack-ai/assets/47415114/3afe6087-d1b0-4389-97b0-bfcaa72d3904)
  
  ![image](https://github.com/ii-pewpewpew-ii/hack-ai/assets/47415114/df34b223-04c6-47c9-82af-ea13b002936b)


