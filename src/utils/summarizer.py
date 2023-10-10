from dotenv import load_dotenv
from newspaper import Article
import os
import openai
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.llms.openai import OpenAI
from langchain.chains.summarize import load_summarize_chain

load_dotenv('.\.env')

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, 'Open-AI api key not found.'

def text_extractor_from_website(url):

    '''
    This function is used to extract the summary of the news article taken from the NEWS API.
    The news article is downloaded and the text content alone is parsed. The parsed content is
    summarized using the built-in nlp module

    Args :
        url (str): An url of a news article

    Returns:
        summary (str) : Summary of the content parsed from the news article
    '''
    
    news_article = Article(url, language="en")
    news_article.download()
    news_article.parse()
    news_article.nlp()
    summary=news_article.summary
    return summary

def generate_summary(txt, curr1, curr2):

    '''
    This functions generates the possible reasons for the change in currency rate, based on
    the summary taken from the news articles. OpenAI API is used to call the prompt model to 
    summarize the content as possible reasons in the given PROMPT_TEMPLATE format.

    Args:
        txt (str) : The summarized text content of all the articles
        curr1 (str) : The base currency, to be used in the prompt
        curr2 (str) : The foreign currency, to be used in the prompt
    
    Returns:
        summarized_content (str) : Possible reasons for the exchange-rate change in points format
    '''
    
    prompt_template = """
    Here is a summary of some articles. Can you summarize this based on how {currency1} and {currency2}'s currency
    rates are changing. And list the reasons as numbered points
    {text}

    SUMMARY:""".format(currency1=curr1, currency2=curr2, text=txt)

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt_template,
        max_tokens=200,  # Maximum token length of summary
        api_key=OPENAI_API_KEY
    )

    # The summary is taken from the response object
    summarized_content = response.choices[0].text

    return summarized_content
