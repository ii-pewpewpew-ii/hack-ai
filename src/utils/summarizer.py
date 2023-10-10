from dotenv import load_dotenv
from newspaper import Article
import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.llms.openai import OpenAI
from langchain.chains.summarize import load_summarize_chain

load_dotenv('.\.env')

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY, 'Open-AI api key not found.'

def text_extractor_from_website(url):
    news_article = Article(url, language="en")
    news_article.download()
    news_article.parse()
    news_article.nlp()
    return news_article.summary

def generate_summary(txt, curr1, curr2):
    llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
    # text_splitter = CharacterTextSplitter()
    # texts = text_splitter.split_text(txt)
    # docs = [Document(page_content=t) for t in texts]
    # chain = load_summarize_chain(llm, chain_type='map_reduce')
    # return chain.run(docs)
    return "Nada"
    # try:
    #     prompt_template = """
    #     Here is a summary of some articles. Can you summarize this based on how {currency1} and {currency2}'s currency
    #     rates are changing. And list the reasons as numbered points
    #     {text}

    #     SUMMARY:""".format(currency1=curr1, currency2=curr2, text=txt)
    #     PROMPT = PromptTemplate(template=prompt_template, input_variables=["currency1", "currency2","text"])
    #     chain = load_summarize_chain(llm, chain_type="map_reduce", map_prompt=PROMPT, combine_prompt=PROMPT)
    # except:
    #     summary = "Something went wrong. \nPlease try with some other document."
    # return summary
